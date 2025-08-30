#!/usr/bin/env python3
"""
Debug Bake SVG

A diagnostic and debugging tool for the SVG color replacement process
used in the StrategyDECK Icon Generation System. This script provides
a visual interface for testing different color combinations and visualizing
the replacement process step by step.
"""

import sys
import os
import argparse
from pathlib import Path
import json
import re
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from typing import Dict, List, Tuple, Optional

# Add the scripts directory to the path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "scripts"))

try:
    from generate_icons import TOKENS, FINISH_COLORS, bake_svg, pick_master
except ImportError:
    print("Error: Could not import generate_icons module. Make sure it exists in the scripts directory.")
    
    # Define fallbacks for testing
    TOKENS = {
        "paper": "#FFFFFF",
        "slate_950": "#060607",
        "brand_orange": "#FF6A00",
        "ink": "#000000",
        "copper": "#B87333",
        "burnt_orange": "#CC5500",
        "matte": "#333333",
        "embossed": "#F5F5F5",
    }
    
    FINISH_COLORS = {
        "flat-orange": "#FF6A00",
        "matte-carbon": "#333333",
        "satin-black": "#000000",
        "burnt-orange": "#CC5500",
        "copper-foil": "#B87333",
        "embossed-paper": "#F5F5F5",
    }
    
    def bake_svg(master_svg: str, mode: str, finish: str) -> str:
        """Fallback implementation of bake_svg"""
        bg = TOKENS["paper"] if mode == "light" else TOKENS["slate_950"]
        fg = FINISH_COLORS.get(finish, TOKENS["brand_orange"])
        svg = master_svg.replace("#FF6A00", bg)  # replace background rect
        svg = svg.replace("#FFFFFF", fg)  # replace icon shapes
        return svg
    
    def pick_master(size_px: int) -> Path:
        """Fallback implementation of pick_master"""
        return Path("assets/masters/strategy_icon_micro.svg")

# Directory setup
ROOT_DIR = SCRIPT_DIR
ASSETS_DIR = ROOT_DIR / "assets"
MASTERS_DIR = ASSETS_DIR / "masters"
OUTPUT_DIR = ASSETS_DIR / "debug"

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class ColorReplacementStep:
    """Represents a single step in the color replacement process"""
    def __init__(self, original: str, replacement: str, description: str):
        self.original = original
        self.replacement = replacement
        self.description = description
        
    def __str__(self) -> str:
        return f"{self.original} → {self.replacement}: {self.description}"

class SVGDebugger(tk.Tk):
    """Interactive SVG debugging tool"""
    def __init__(self):
        super().__init__()
        
        self.title("StrategyDECK SVG Debugger")
        self.geometry("1000x800")
        
        # State variables
        self.master_svg_path = None
        self.master_svg_content = ""
        self.current_svg_content = ""
        self.replacement_steps: List[ColorReplacementStep] = []
        self.mode = tk.StringVar(value="light")
        self.finish = tk.StringVar(value="flat-orange")
        self.custom_colors: Dict[str, str] = {}
        
        # Create UI
        self._create_ui()
        
        # Try to load default master SVG
        default_master = MASTERS_DIR / "strategy_icon_micro.svg"
        if default_master.exists():
            self.load_svg(default_master)
    
    def _create_ui(self):
        """Create the user interface"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create top panel with controls
        control_frame = ttk.LabelFrame(main_frame, text="SVG Controls")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File controls
        file_frame = ttk.Frame(control_frame)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(file_frame, text="SVG File:").pack(side=tk.LEFT, padx=(0, 5))
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, width=50).pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        ttk.Button(file_frame, text="Browse...", command=self._browse_svg).pack(side=tk.LEFT)
        
        # Mode and finish controls
        mode_frame = ttk.Frame(control_frame)
        mode_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Radiobutton(mode_frame, text="Light", variable=self.mode, value="light", command=self._update_preview).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(mode_frame, text="Dark", variable=self.mode, value="dark", command=self._update_preview).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(mode_frame, text="Finish:").pack(side=tk.LEFT, padx=(20, 5))
        finish_combo = ttk.Combobox(mode_frame, textvariable=self.finish, values=list(FINISH_COLORS.keys()), width=15)
        finish_combo.pack(side=tk.LEFT)
        finish_combo.bind("<<ComboboxSelected>>", lambda e: self._update_preview())
        
        # Color control buttons
        color_frame = ttk.Frame(control_frame)
        color_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(color_frame, text="Edit Background Color", command=lambda: self._edit_color("background")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(color_frame, text="Edit Foreground Color", command=lambda: self._edit_color("foreground")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(color_frame, text="Reset Colors", command=self._reset_colors).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(color_frame, text="Bake SVG", command=self._bake_svg).pack(side=tk.RIGHT)
        
        # Create main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - SVG preview
        preview_frame = ttk.LabelFrame(content_frame, text="SVG Preview")
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.preview_canvas = tk.Canvas(preview_frame, bg="white", highlightthickness=0)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Right panel - Color replacements
        replacement_frame = ttk.LabelFrame(content_frame, text="Color Replacement Steps")
        replacement_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0), width=400)
        
        # Replacement listbox
        self.replacement_listbox = tk.Listbox(replacement_frame, font=("Consolas", 10), height=15)
        self.replacement_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Bottom panel with buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Save SVG", command=self._save_svg).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Save PNG", command=self._save_png).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Export Report", command=self._export_report).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Exit", command=self.quit).pack(side=tk.RIGHT)
    
    def _browse_svg(self):
        """Open file browser to select an SVG file"""
        file_path = filedialog.askopenfilename(
            title="Select SVG File",
            filetypes=[("SVG Files", "*.svg"), ("All Files", "*.*")],
            initialdir=MASTERS_DIR
        )
        
        if file_path:
            self.load_svg(Path(file_path))
    
    def load_svg(self, file_path: Path):
        """Load an SVG file"""
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
                
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            self.master_svg_path = file_path
            self.master_svg_content = content
            self.current_svg_content = content
            self.file_path_var.set(str(file_path))
            
            # Update preview
            self._update_preview()
            
            self.status_var.set(f"Loaded SVG: {file_path.name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load SVG: {e}")
            self.status_var.set(f"Error: {e}")
    
    def _update_preview(self):
        """Update the SVG preview"""
        if not self.master_svg_content:
            return
            
        try:
            # Apply color replacements
            baked_svg = self._apply_replacements()
            self.current_svg_content = baked_svg
            
            # Save to temp file for preview
            temp_path = OUTPUT_DIR / "temp_preview.svg"
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(baked_svg)
                
            # Clear canvas
            self.preview_canvas.delete("all")
            
            # Try to load SVG preview (requires PIL)
            try:
                from PIL import Image, ImageTk
                
                # Try to convert SVG to PNG for preview
                import cairosvg
                png_data = cairosvg.svg2png(bytestring=baked_svg.encode("utf-8"))
                
                image = Image.open(io.BytesIO(png_data))
                photo = ImageTk.PhotoImage(image)
                
                # Calculate centered position
                canvas_width = self.preview_canvas.winfo_width()
                canvas_height = self.preview_canvas.winfo_height()
                x = max(0, (canvas_width - photo.width()) // 2)
                y = max(0, (canvas_height - photo.height()) // 2)
                
                self.preview_canvas.create_image(x, y, anchor=tk.NW, image=photo)
                self.preview_canvas.image = photo  # Keep reference
            except (ImportError, Exception) as e:
                # Fallback to displaying SVG code
                self.preview_canvas.create_text(
                    10, 10, 
                    text=f"Preview not available: {e}\n\n{baked_svg[:500]}...", 
                    anchor=tk.NW,
                    fill="black"
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update preview: {e}")
            self.status_var.set(f"Error: {e}")
    
    def _apply_replacements(self) -> str:
        """Apply color replacements and track steps"""
        if not self.master_svg_content:
            return ""
            
        # Start with original content
        content = self.master_svg_content
        self.replacement_steps = []
        
        # Determine background and foreground colors
        mode = self.mode.get()
        finish = self.finish.get()
        
        bg_color = self.custom_colors.get("background", 
                   TOKENS["paper"] if mode == "light" else TOKENS["slate_950"])
        
        fg_color = self.custom_colors.get("foreground",
                   FINISH_COLORS.get(finish, TOKENS["brand_orange"]))
        
        # Replace background color (#FF6A00)
        self.replacement_steps.append(
            ColorReplacementStep("#FF6A00", bg_color, "Background replacement")
        )
        content = content.replace("#FF6A00", bg_color)
        
        # Replace foreground color (#FFFFFF)
        self.replacement_steps.append(
            ColorReplacementStep("#FFFFFF", fg_color, "Foreground replacement")
        )
        content = content.replace("#FFFFFF", fg_color)
        
        # Update listbox
        self.replacement_listbox.delete(0, tk.END)
        for i, step in enumerate(self.replacement_steps, 1):
            self.replacement_listbox.insert(tk.END, f"{i}. {step}")
        
        return content
    
    def _edit_color(self, color_type: str):
        """Open color picker dialog to edit a color"""
        current_color = self.custom_colors.get(
            color_type,
            TOKENS["paper"] if color_type == "background" and self.mode.get() == "light" else
            TOKENS["slate_950"] if color_type == "background" else
            FINISH_COLORS.get(self.finish.get(), TOKENS["brand_orange"])
        )
        
        color = colorchooser.askcolor(
            title=f"Select {color_type.capitalize()} Color",
            initialcolor=current_color
        )
        
        if color and color[1]:
            self.custom_colors[color_type] = color[1]
            self._update_preview()
            self.status_var.set(f"Updated {color_type} color to {color[1]}")
    
    def _reset_colors(self):
        """Reset to default colors"""
        self.custom_colors = {}
        self._update_preview()
        self.status_var.set("Reset to default colors")
    
    def _bake_svg(self):
        """Bake SVG using the generate_icons module"""
        if not self.master_svg_content:
            messagebox.showerror("Error", "No SVG loaded")
            return
            
        try:
            # Bake SVG using module function
            mode = self.mode.get()
            finish = self.finish.get()
            
            baked_svg = bake_svg(self.master_svg_content, mode, finish)
            self.current_svg_content = baked_svg
            
            # Track replacement steps
            bg_color = TOKENS["paper"] if mode == "light" else TOKENS["slate_950"]
            fg_color = FINISH_COLORS.get(finish, TOKENS["brand_orange"])
            
            self.replacement_steps = [
                ColorReplacementStep("#FF6A00", bg_color, "Background replacement (bake_svg)"),
                ColorReplacementStep("#FFFFFF", fg_color, "Foreground replacement (bake_svg)")
            ]
            
            # Update preview
            self._update_preview()
            
            self.status_var.set(f"Baked SVG with mode={mode}, finish={finish}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to bake SVG: {e}")
            self.status_var.set(f"Error: {e}")
    
    def _save_svg(self):
        """Save current SVG to file"""
        if not self.current_svg_content:
            messagebox.showerror("Error", "No SVG to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save SVG File",
            defaultextension=".svg",
            filetypes=[("SVG Files", "*.svg"), ("All Files", "*.*")],
            initialdir=OUTPUT_DIR
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.current_svg_content)
                    
                self.status_var.set(f"Saved SVG to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save SVG: {e}")
                self.status_var.set(f"Error: {e}")
    
    def _save_png(self):
        """Save current SVG as PNG"""
        if not self.current_svg_content:
            messagebox.showerror("Error", "No SVG to save")
            return
            
        try:
            import cairosvg
        except ImportError:
            messagebox.showerror("Error", "CairoSVG is required for PNG export. Please install with 'pip install cairosvg'")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save PNG File",
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")],
            initialdir=OUTPUT_DIR
        )
        
        if file_path:
            try:
                # Convert SVG to PNG
                cairosvg.svg2png(
                    bytestring=self.current_svg_content.encode("utf-8"),
                    write_to=file_path
                )
                
                self.status_var.set(f"Saved PNG to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save PNG: {e}")
                self.status_var.set(f"Error: {e}")
    
    def _export_report(self):
        """Export debugging report"""
        if not self.master_svg_path:
            messagebox.showerror("Error", "No SVG loaded")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export Debug Report",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialdir=OUTPUT_DIR
        )
        
        if file_path:
            try:
                mode = self.mode.get()
                finish = self.finish.get()
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("StrategyDECK SVG Debug Report\n")
                    f.write("============================\n\n")
                    
                    f.write(f"Master SVG: {self.master_svg_path}\n")
                    f.write(f"Mode: {mode}\n")
                    f.write(f"Finish: {finish}\n\n")
                    
                    f.write("Custom Colors:\n")
                    for color_type, color in self.custom_colors.items():
                        f.write(f"  {color_type}: {color}\n")
                    f.write("\n")
                    
                    f.write("Color Replacement Steps:\n")
                    for i, step in enumerate(self.replacement_steps, 1):
                        f.write(f"  {i}. {step.original} → {step.replacement}: {step.description}\n")
                    f.write("\n")
                    
                    f.write("Original SVG Content:\n")
                    f.write("---------------------\n")
                    f.write(self.master_svg_content[:1000])
                    if len(self.master_svg_content) > 1000:
                        f.write("...\n")
                    f.write("\n\n")
                    
                    f.write("Baked SVG Content:\n")
                    f.write("------------------\n")
                    f.write(self.current_svg_content[:1000])
                    if len(self.current_svg_content) > 1000:
                        f.write("...\n")
                
                self.status_var.set(f"Exported debug report to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report: {e}")
                self.status_var.set(f"Error: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Debug SVG baking process")
    parser.add_argument("--svg", help="Path to SVG file to debug")
    parser.add_argument("--mode", choices=["light", "dark"], default="light", help="Icon mode")
    parser.add_argument("--finish", default="flat-orange", help="Icon finish")
    parser.add_argument("--output", help="Output path for baked SVG")
    parser.add_argument("--gui", action="store_true", help="Launch GUI debugger")
    
    args = parser.parse_args()
    
    # Always launch GUI if no arguments or --gui specified
    if args.gui or (not args.svg and not args.output):
        app = SVGDebugger()
        
        # Load SVG if specified
        if args.svg:
            app.load_svg(Path(args.svg))
            app.mode.set(args.mode)
            app.finish.set(args.finish)
            app._update_preview()
        
        app.mainloop()
        return
    
    # Command-line mode
    if not args.svg:
        print("Error: --svg argument is required in command-line mode")
        parser.print_help()
        return
        
    svg_path = Path(args.svg)
    if not svg_path.exists():
        print(f"Error: SVG file not found: {svg_path}")
        return
        
    try:
        # Load SVG
        with open(svg_path, "r", encoding="utf-8") as f:
            master_svg = f.read()
            
        # Bake SVG
        baked_svg = bake_svg(master_svg, args.mode, args.finish)
        
        # Save output or print to console
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(baked_svg)
                
            print(f"Baked SVG saved to {output_path}")
        else:
            print(baked_svg)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
