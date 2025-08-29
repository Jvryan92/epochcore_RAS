"""
PROTECTED FILE - EPOCHCORE RAS STRIPE INTEGRATION
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional

import stripe

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stripe_transactions.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('epochcore_stripe')


@dataclass
class StripeProduct:
    name: str
    price_id: str  # Stripe price ID
    product_id: str  # Stripe product ID
    revenue_type: str
    revenue_share: Decimal


class EpochCoreStripeManager:
    def __init__(self):
        # Never commit API keys - load from environment
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

        # Revenue sharing configuration
        self.revenue_shares = {
            'GAME_SALE': Decimal('1.00'),  # 100% to EpochCore
            'IN_APP': Decimal('0.70'),     # 70% after platform
            'CREATOR': Decimal('0.90'),    # 90% to EpochCore
            'ENTERPRISE': Decimal('1.00')  # 100% to EpochCore
        }

        # Product configurations (to be set up in Stripe dashboard)
        self.products = {
            'game_base': StripeProduct(
                name='EpochCore Game',
                price_id='price_xxxxx',  # Replace with actual Stripe price ID
                product_id='prod_xxxxx',  # Replace with actual Stripe product ID
                revenue_type='GAME_SALE',
                revenue_share=self.revenue_shares['GAME_SALE']
            ),
            'season_pass': StripeProduct(
                name='Season Pass',
                price_id='price_xxxxx',
                product_id='prod_xxxxx',
                revenue_type='IN_APP',
                revenue_share=self.revenue_shares['IN_APP']
            ),
            'creator_subscription': StripeProduct(
                name='Creator Platform Access',
                price_id='price_xxxxx',
                product_id='prod_xxxxx',
                revenue_type='CREATOR',
                revenue_share=self.revenue_shares['CREATOR']
            ),
            'enterprise_license': StripeProduct(
                name='Enterprise License',
                price_id='price_xxxxx',
                product_id='prod_xxxxx',
                revenue_type='ENTERPRISE',
                revenue_share=self.revenue_shares['ENTERPRISE']
            )
        }

    async def create_payment_intent(self,
                                    product_key: str,
                                    quantity: int = 1,
                                    customer_id: Optional[str] = None) -> Dict:
        """Create a Stripe PaymentIntent for a purchase"""
        try:
            product = self.products[product_key]

            # Calculate amount with revenue share
            price = await self.get_product_price(product.price_id)
            total_amount = price * quantity

            payment_intent = stripe.PaymentIntent.create(
                amount=int(total_amount * 100),  # Convert to cents
                currency='usd',
                customer=customer_id,
                metadata={
                    'product_key': product_key,
                    'quantity': quantity,
                    'revenue_type': product.revenue_type,
                    'revenue_share': float(product.revenue_share)
                }
            )

            logger.info(f"Created PaymentIntent for {product_key}: {payment_intent.id}")
            return payment_intent

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating PaymentIntent: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Error creating PaymentIntent: {str(e)}")
            raise

    async def handle_webhook(self, payload: bytes, sig_header: str) -> Dict:
        """Handle Stripe webhooks for payment events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )

            # Handle successful payments
            if event.type == 'payment_intent.succeeded':
                return await self.process_successful_payment(event.data.object)

            # Handle refunds
            elif event.type == 'charge.refunded':
                return await self.process_refund(event.data.object)

            # Handle disputes
            elif event.type == 'charge.dispute.created':
                return await self.process_dispute(event.data.object)

            logger.info(f"Processed webhook event: {event.type}")
            return {'status': 'success', 'type': event.type}

        except stripe.error.SignatureVerificationError:
            logger.error("Invalid webhook signature")
            raise

        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            raise

    async def process_successful_payment(self, payment_intent: Dict) -> Dict:
        """Process a successful payment"""
        try:
            metadata = payment_intent.metadata
            product_key = metadata.get('product_key')
            quantity = int(metadata.get('quantity', 1))
            revenue_type = metadata.get('revenue_type')
            revenue_share = Decimal(metadata.get('revenue_share'))

            # Calculate revenue shares
            amount = payment_intent.amount / 100  # Convert from cents
            platform_fee = self._calculate_platform_fee(amount, revenue_type)
            net_revenue = amount - platform_fee

            # Record transaction
            transaction = {
                'payment_intent_id': payment_intent.id,
                'amount': amount,
                'platform_fee': platform_fee,
                'net_revenue': net_revenue,
                'product_key': product_key,
                'quantity': quantity,
                'revenue_type': revenue_type,
                'timestamp': datetime.now().isoformat()
            }

            # Save transaction record
            await self._save_transaction(transaction)

            logger.info(f"Processed successful payment: {payment_intent.id}")
            return transaction

        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}")
            raise

    async def get_revenue_report(self,
                                 start_date: datetime,
                                 end_date: datetime) -> Dict:
        """Generate revenue report for date range"""
        try:
            charges = stripe.Charge.list(
                created={
                    'gte': int(start_date.timestamp()),
                    'lte': int(end_date.timestamp())
                }
            )

            report = {
                'total_revenue': Decimal('0'),
                'platform_fees': Decimal('0'),
                'net_revenue': Decimal('0'),
                'by_type': {},
                'transaction_count': 0
            }

            for charge in charges.auto_paging_iter():
                if charge.paid and not charge.refunded:
                    amount = Decimal(str(charge.amount / 100))
                    revenue_type = charge.metadata.get('revenue_type', 'OTHER')

                    if revenue_type not in report['by_type']:
                        report['by_type'][revenue_type] = Decimal('0')

                    report['by_type'][revenue_type] += amount
                    report['total_revenue'] += amount
                    report['transaction_count'] += 1

                    # Calculate platform fee
                    platform_fee = self._calculate_platform_fee(
                        amount,
                        revenue_type
                    )
                    report['platform_fees'] += platform_fee

            report['net_revenue'] = report['total_revenue'] - report['platform_fees']

            logger.info(f"Generated revenue report: {start_date} to {end_date}")
            return report

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error generating report: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise

    def _calculate_platform_fee(self,
                                amount: Decimal,
                                revenue_type: str) -> Decimal:
        """Calculate platform fee based on revenue type"""
        if revenue_type not in self.revenue_shares:
            return Decimal('0')

        revenue_share = self.revenue_shares[revenue_type]
        return amount * (Decimal('1') - revenue_share)

    async def _save_transaction(self, transaction: Dict) -> None:
        """Save transaction record to file"""
        try:
            path = Path('transactions')
            path.mkdir(exist_ok=True)

            file_path = path / f"{transaction['timestamp'][:10]}.jsonl"

            with open(file_path, 'a') as f:
                f.write(f"{str(transaction)}\n")

        except Exception as e:
            logger.error(f"Error saving transaction: {str(e)}")
            raise


# Usage example (with environment variables set):
if __name__ == "__main__":
    stripe_manager = EpochCoreStripeManager()

    # Example: Create a payment intent for game purchase
    # payment_intent = await stripe_manager.create_payment_intent('game_base')

    # Example: Generate revenue report
    # start_date = datetime.now() - timedelta(days=30)
    # report = await stripe_manager.get_revenue_report(start_date, datetime.now())
