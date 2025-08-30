#!/usr/bin/env python3
"""
StrategyDECK Icon Report Visualizer

Generates an HTML visualization of the icon generation report.
"""

import argparse
import json
import os
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

# Add the scripts directory to the path
SCRIPT_DIR = Path(__file__).resolve().parent / "scripts"
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

# Report directories
REPORT_DIR = ROOT / "reports"
OUTPUT_DIR = REPORT_DIR / "html"

# Create output directory
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_html_report(report_path, output_path=None):
    """Generate an HTML visualization of the report"""
    # Load the report data
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
    except Exception as e:
        print(f"Error loading report: {e}")
        return None

    # Generate timestamp for the report
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Generate the HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StrategyDECK Icon Generation Report</title>
    <style>
        :root {{
            --primary-color: #FF6A00;
            --secondary-color: #060607;
            --success-color: #2ECC71;
            --warning-color: #F39C12;
            --danger-color: #E74C3C;
            --light-color: #ECF0F1;
            --dark-color: #2C3E50;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: var(--dark-color);
            background-color: #f8f9fa;
            margin: 0;
            padding: 0;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background-color: var(--primary-color);
            color: white;
            padding: 20px;
            text-align: center;
            margin-bottom: 30px;
            border-radius: 5px;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 0;
            font-weight: 600;
        }}
        
        .card {{
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            overflow: hidden;
        }}
        
        .card-header {{
            padding: 15px 20px;
            background-color: var(--secondary-color);
            color: white;
            font-weight: 600;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .card-body {{
            padding: 20px;
        }}
        
        .progress {{
            height: 20px;
            background-color: #e0e0e0;
            border-radius: 5px;
            margin-bottom: 10px;
            overflow: hidden;
        }}
        
        .progress-bar {{
            height: 100%;
            background-color: var(--primary-color);
            border-radius: 5px;
            color: white;
            text-align: center;
            line-height: 20px;
            font-size: 12px;
        }}
        
        .progress-bar-success {{
            background-color: var(--success-color);
        }}
        
        .progress-bar-warning {{
            background-color: var(--warning-color);
        }}
        
        .progress-bar-danger {{
            background-color: var(--danger-color);
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: 600;
            margin-right: 5px;
        }}
        
        .badge-success {{
            background-color: var(--success-color);
            color: white;
        }}
        
        .badge-warning {{
            background-color: var(--warning-color);
            color: white;
        }}
        
        .badge-danger {{
            background-color: var(--danger-color);
            color: white;
        }}
        
        .badge-info {{
            background-color: var(--primary-color);
            color: white;
        }}
        
        .badge-secondary {{
            background-color: var(--secondary-color);
            color: white;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        th {{
            background-color: var(--light-color);
            font-weight: 600;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: var(--dark-color);
            border-top: 1px solid #e0e0e0;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .stat-card {{
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            padding: 20px;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 10px;
            color: var(--primary-color);
        }}
        
        .stat-label {{
            font-size: 14px;
            color: var(--dark-color);
            margin-bottom: 0;
        }}
        
        .theme-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }}
        
        .theme-badge {{
            padding: 5px 10px;
            border-radius: 15px;
            background-color: var(--primary-color);
            color: white;
            font-size: 12px;
        }}
        
        .issues-list {{
            max-height: 200px;
            overflow-y: auto;
            background-color: var(--light-color);
            border-radius: 5px;
            padding: 10px;
        }}
        
        .issue-item {{
            padding: 5px 0;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .issue-item:last-child {{
            border-bottom: none;
        }}
    </style>
</head>
<body>
    <header>
        <h1>StrategyDECK Icon Generation Report</h1>
        <p>Generated on {timestamp}</p>
    </header>
    
    <div class="container">
        <!-- Summary Overview -->
        <div class="card">
            <div class="card-header">
                <h2>Summary Overview</h2>
            </div>
            <div class="card-body">
                <div class="grid">
                    <div class="stat-card">
                        <div class="stat-value">{report_data['counts']['svg_total']}</div>
                        <div class="stat-label">Total SVG Files</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{report_data['counts']['png_total']}</div>
                        <div class="stat-label">Total PNG Files</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{report_data['variants']['total']}</div>
                        <div class="stat-label">Expected Variants</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{report_data['counts']['svg_variants']}</div>
                        <div class="stat-label">SVG Variants Found</div>
                    </div>
                </div>
                
                <h3>Variant Generation Progress</h3>
                <div class="progress">
"""

    # SVG progress bar
    svg_percentage = 0
    if report_data['variants']['total'] > 0:
        svg_percentage = round(
            (report_data['counts']['svg_variants'] / report_data['variants']['total']) * 100)

    svg_class = "progress-bar"
    if svg_percentage >= 90:
        svg_class += " progress-bar-success"
    elif svg_percentage >= 50:
        svg_class += " progress-bar-warning"
    else:
        svg_class += " progress-bar-danger"

    html += f"""
                    <div class="{svg_class}" style="width: {svg_percentage}%">
                        {svg_percentage}% SVG
                    </div>
                </div>
"""

    # PNG progress bar
    png_percentage = 0
    if report_data['variants']['total'] > 0:
        png_percentage = round(
            (report_data['counts']['png_variants'] / report_data['variants']['total']) * 100)

    png_class = "progress-bar"
    if png_percentage >= 90:
        png_class += " progress-bar-success"
    elif png_percentage >= 50:
        png_class += " progress-bar-warning"
    else:
        png_class += " progress-bar-danger"

    html += f"""
                <div class="progress">
                    <div class="{png_class}" style="width: {png_percentage}%">
                        {png_percentage}% PNG
                    </div>
                </div>
                
                <h3>CairoSVG Status</h3>
                <p>
                    <span class="badge {'badge-success' if report_data['validation']['has_cairosvg'] else 'badge-danger'}">
                        {'Installed' if report_data['validation']['has_cairosvg'] else 'Not Installed'}
                    </span>
                    {'' if report_data['validation']['has_cairosvg'] else 'CairoSVG is required for PNG conversion. Install with: pip install cairosvg'}
                </p>
            </div>
        </div>
        
        <!-- Variant Details -->
        <div class="card">
            <div class="card-header">
                <h2>Variant Details</h2>
            </div>
            <div class="card-body">
                <table>
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Expected Variants</td>
                            <td>{report_data['variants']['total']}</td>
                        </tr>
                        <tr>
                            <td>Found SVG Variants</td>
                            <td>{report_data['counts']['svg_variants']}</td>
                        </tr>
                        <tr>
                            <td>Found PNG Variants</td>
                            <td>{report_data['counts']['png_variants']}</td>
                        </tr>
                        <tr>
                            <td>Missing SVG Variants</td>
                            <td>{report_data['counts']['missing_svg']}</td>
                        </tr>
                        <tr>
                            <td>Missing PNG Variants</td>
                            <td>{report_data['counts']['missing_png']}</td>
                        </tr>
                    </tbody>
                </table>
                
                <h3>Example Variants</h3>
                <div class="issues-list">
"""

    # Add example variants
    for variant in report_data['variants']['examples']:
        html += f"""
                    <div class="issue-item">
                        {variant.get('mode', '')}/{variant.get('finish', '')}/{variant.get('size', '')}px/{variant.get('context', '')}
                    </div>
"""

    html += """
                </div>
            </div>
        </div>
        
        <!-- Master Files -->
        <div class="card">
            <div class="card-header">
                <h2>Master Files</h2>
            </div>
            <div class="card-body">
                <table>
                    <thead>
                        <tr>
                            <th>File</th>
                            <th>Status</th>
                            <th>Size</th>
                        </tr>
                    </thead>
                    <tbody>
"""

    # Add master file details
    master_report = report_data['master_files']

    html += f"""
                        <tr>
                            <td>strategy_icon_micro.svg</td>
                            <td>
                                <span class="badge {'badge-success' if master_report['micro_exists'] else 'badge-danger'}">
                                    {'Exists' if master_report['micro_exists'] else 'Missing'}
                                </span>
                            </td>
                            <td>{master_report['micro_size']} bytes</td>
                        </tr>
                        <tr>
                            <td>strategy_icon_standard.svg</td>
                            <td>
                                <span class="badge {'badge-success' if master_report['standard_exists'] else 'badge-danger'}">
                                    {'Exists' if master_report['standard_exists'] else 'Missing'}
                                </span>
                            </td>
                            <td>{master_report['standard_size']} bytes</td>
                        </tr>
                    </tbody>
                </table>
"""

    # Add master file issues if any
    if master_report['issues']:
        html += """
                <h3>Master File Issues</h3>
                <div class="issues-list">
"""

        for issue in master_report['issues']:
            html += f"""
                    <div class="issue-item">
                        {issue['file']}: {issue['issue']}
                    </div>
"""

        html += """
                </div>
"""

    html += """
            </div>
        </div>
"""

    # Add Endless Glyph System details if exists
    glyph_report = report_data['endless_glyph']

    if glyph_report['exists']:
        html += """
        <!-- Endless Glyph System -->
        <div class="card">
            <div class="card-header">
                <h2>Endless Glyph System</h2>
            </div>
            <div class="card-body">
"""

        html += f"""
                <p>Status: <span class="badge badge-success">Installed</span></p>
                <p>Theme Count: <span class="badge badge-info">{glyph_report['theme_count']}</span></p>
                
                <h3>Available Themes</h3>
                <div class="theme-list">
"""

        # Add theme badges
        for theme in glyph_report['themes']:
            html += f"""
                    <span class="theme-badge">{theme}</span>
"""

        html += """
                </div>
"""

        # Add issues if any
        if glyph_report['issues']:
            html += """
                <h3>Glyph System Issues</h3>
                <div class="issues-list">
"""

            for issue in glyph_report['issues']:
                html += f"""
                    <div class="issue-item">
                        {issue['issue']}
                    </div>
"""

            html += """
                </div>
"""

        html += """
            </div>
        </div>
"""

    # Add SVG Quality section if exists
    if 'svg_quality' in report_data:
        svg_quality = report_data['svg_quality']

        html += """
        <!-- SVG Quality -->
        <div class="card">
            <div class="card-header">
                <h2>SVG Quality</h2>
            </div>
            <div class="card-body">
"""

        # Calculate valid percentage
        valid_percentage = 0
        if svg_quality['total_files'] > 0:
            valid_percentage = round(
                (svg_quality['valid_files'] / svg_quality['total_files']) * 100)

        quality_class = "progress-bar"
        if valid_percentage >= 90:
            quality_class += " progress-bar-success"
        elif valid_percentage >= 70:
            quality_class += " progress-bar-warning"
        else:
            quality_class += " progress-bar-danger"

        html += f"""
                <div class="progress">
                    <div class="{quality_class}" style="width: {valid_percentage}%">
                        {valid_percentage}% Valid
                    </div>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Total Files Checked</td>
                            <td>{svg_quality['total_files']}</td>
                        </tr>
                        <tr>
                            <td>Valid Files</td>
                            <td>{svg_quality['valid_files']}</td>
                        </tr>
                        <tr>
                            <td>Invalid Files</td>
                            <td>{svg_quality['invalid_files']}</td>
                        </tr>
                        <tr>
                            <td>Empty Files</td>
                            <td>{svg_quality['empty_files']}</td>
                        </tr>
                        <tr>
                            <td>Missing viewBox</td>
                            <td>{svg_quality['missing_viewbox']}</td>
                        </tr>
                    </tbody>
                </table>
"""

        # Add issues if any
        if svg_quality['issues']:
            html += """
                <h3>SVG Issues</h3>
                <div class="issues-list">
"""

            for issue in svg_quality['issues']:
                html += f"""
                    <div class="issue-item">
                        {issue['file']}: {issue['issue']}
                    </div>
"""

            html += """
                </div>
"""

        html += """
            </div>
        </div>
"""

    # Add PNG Quality section if exists
    if 'png_quality' in report_data:
        png_quality = report_data['png_quality']

        html += """
        <!-- PNG Quality -->
        <div class="card">
            <div class="card-header">
                <h2>PNG Quality</h2>
            </div>
            <div class="card-body">
"""

        # Calculate valid percentage
        valid_percentage = 0
        if png_quality['total_files'] > 0:
            valid_percentage = round(
                (png_quality['valid_files'] / png_quality['total_files']) * 100)

        quality_class = "progress-bar"
        if valid_percentage >= 90:
            quality_class += " progress-bar-success"
        elif valid_percentage >= 70:
            quality_class += " progress-bar-warning"
        else:
            quality_class += " progress-bar-danger"

        html += f"""
                <div class="progress">
                    <div class="{quality_class}" style="width: {valid_percentage}%">
                        {valid_percentage}% Valid
                    </div>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Total Files Checked</td>
                            <td>{png_quality['total_files']}</td>
                        </tr>
                        <tr>
                            <td>Valid Files</td>
                            <td>{png_quality['valid_files']}</td>
                        </tr>
                        <tr>
                            <td>Invalid Files</td>
                            <td>{png_quality['invalid_files']}</td>
                        </tr>
                        <tr>
                            <td>Empty Files</td>
                            <td>{png_quality['empty_files']}</td>
                        </tr>
                    </tbody>
                </table>
"""

        # Add issues if any
        if png_quality['issues']:
            html += """
                <h3>PNG Issues</h3>
                <div class="issues-list">
"""

            for issue in png_quality['issues']:
                html += f"""
                    <div class="issue-item">
                        {issue['file']}: {issue['issue']}
                    </div>
"""

            html += """
                </div>
"""

        html += """
            </div>
        </div>
"""

    # Add Suggested Solutions section
    html += """
        <!-- Suggested Solutions -->
        <div class="card">
            <div class="card-header">
                <h2>Suggested Solutions</h2>
            </div>
            <div class="card-body">
                <ol>
"""

    # Add general solutions
    html += """
                    <li>Run the clean rebuild script: <code>./clean_rebuild_assets.sh</code></li>
                    <li>Check master SVG files for correct color tokens</li>
                    <li>Validate the variant matrix CSV file</li>
"""

    # Add PNG-specific solutions if needed
    if report_data['validation']['has_cairosvg'] and report_data['counts']['png_variants'] < report_data['variants']['total']:
        html += """
                    <li>Debug PNG conversion: <code>python debug_png_conversion.py --report</code></li>
"""

    # Add CairoSVG installation if not installed
    if not report_data['validation']['has_cairosvg']:
        html += """
                    <li>Install CairoSVG for PNG conversion: <code>pip install cairosvg</code></li>
"""

    html += """
                </ol>
                
                <h3>Diagnostic Tools</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Tool</th>
                            <th>Purpose</th>
                            <th>Command</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>PNG Conversion Debug</td>
                            <td>Diagnose PNG conversion issues</td>
                            <td><code>python debug_png_conversion.py</code></td>
                        </tr>
                        <tr>
                            <td>SVG Baking Debug</td>
                            <td>Test SVG color replacement</td>
                            <td><code>python debug_bake_svg_cli.py --svg PATH</code></td>
                        </tr>
                        <tr>
                            <td>Clean and Rebuild</td>
                            <td>Completely rebuild all assets</td>
                            <td><code>./clean_rebuild_assets.sh</code></td>
                        </tr>
                        <tr>
                            <td>Icon Report</td>
                            <td>Generate this report</td>
                            <td><code>python icon_report.py</code></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="footer">
            <p>StrategyDECK Icon Generation System &copy; 2025</p>
        </div>
    </div>
</body>
</html>
"""

    # Write the HTML to file
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"icon_report_{timestamp}.html"
    else:
        output_path = Path(output_path)

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"HTML report generated: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error generating HTML report: {e}")
        return None


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate HTML visualization of icon report")
    parser.add_argument("report", help="Path to JSON report file")
    parser.add_argument("--output", help="Output path for HTML report")
    parser.add_argument("--open", action="store_true",
                        help="Open the report in a browser after generation")

    args = parser.parse_args()

    # Check if report exists
    report_path = Path(args.report)
    if not report_path.exists():
        print(f"Error: Report file not found: {report_path}")
        return 1

    # Generate HTML report
    output_path = generate_html_report(report_path, args.output)

    if output_path and args.open:
        # Open in browser
        try:
            webbrowser.open(f"file://{output_path.absolute()}")
            print(f"Opened report in browser")
        except Exception as e:
            print(f"Error opening report in browser: {e}")

    return 0 if output_path else 1


if __name__ == "__main__":
    sys.exit(main())
