import 
import ultra_trigger

BATCH_TRIGGERS = [
    "QUORUMCALL🗳️",
    "AUTOCOMPOUND⏩",
    "PRIMALGLYPH🐉",
    "WORLDRAID⚔️",
    "METAFORGE⚙️",
    "CAPSULEFUSION💥",
    "CROWNSEAL👑"
]

def main():
    for trigger in BATCH_TRIGGERS:
        try:
            print(f"Minting capsule for trigger: {trigger}")
            ultra_trigger.generate_capsule(trigger)
        except Exception as e:
            print(f"Error minting capsule for {trigger}: {e}")
        try:
            print(f"Minting capsule for trigger: {trigger}")
            ultra_trigger.generate_capsule(trigger)
        except Exception as e:
            print(f"Error minting capsule for {trigger}: {e}")
        print(f"Minting capsule for trigger: {trigger}")
        ultra_trigger.generate_capsule(trigger)

if __name__ == "__main__":
    main()
