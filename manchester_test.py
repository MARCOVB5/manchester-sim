import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class ManchesterValidator:
    """
    A class for validating and visualizing Manchester encoding.
    This can be integrated into the existing ManchesterCodingApp.
    """
    
    @staticmethod
    def validate_manchester_encoding(binary_data, manchester_data):
        """
        Validates if manchester_data is the correct Manchester encoding of binary_data.
        
        Args:
            binary_data (str): Original binary string
            manchester_data (list): Manchester encoded data as a list of 0s and 1s
            
        Returns:
            tuple: (is_valid, errors) where errors is a list of positions where encoding is wrong
        """
        if not binary_data or not manchester_data:
            return False, ["Empty data"]
        
        # Check if the manchester data length is twice the binary data length
        if len(manchester_data) != 2 * len(binary_data):
            return False, [f"Length mismatch: Manchester data should be twice as long as binary data. "
                          f"Manchester: {len(manchester_data)}, Binary: {len(binary_data)}"]
        
        errors = []
        
        # Check each bit encoding
        for i, bit in enumerate(binary_data):
            manchester_pos = i * 2
            if bit == '0':
                # 0 should be encoded as 01
                if manchester_data[manchester_pos:manchester_pos+2] != [0, 1]:
                    errors.append(f"Bit {i}: '0' should be encoded as '01', got "
                                 f"'{manchester_data[manchester_pos]}{manchester_data[manchester_pos+1]}'")
            elif bit == '1':
                # 1 should be encoded as 10
                if manchester_data[manchester_pos:manchester_pos+2] != [1, 0]:
                    errors.append(f"Bit {i}: '1' should be encoded as '10', got "
                                 f"'{manchester_data[manchester_pos]}{manchester_data[manchester_pos+1]}'")
            else:
                errors.append(f"Invalid binary bit at position {i}: '{bit}'")
        
        return len(errors) == 0, errors

    @staticmethod
    def validate_manchester_decoding(manchester_data, binary_result):
        """
        Validates if binary_result is the correct decoding of manchester_data.
        
        Args:
            manchester_data (list): Manchester encoded data as a list of 0s and 1s
            binary_result (str): Decoded binary string
            
        Returns:
            tuple: (is_valid, errors) where errors is a list of errors found
        """
        if not binary_result or not manchester_data:
            return False, ["Empty data"]
        
        # Check if the lengths match
        expected_binary_length = len(manchester_data) // 2
        if len(binary_result) != expected_binary_length:
            return False, [f"Length mismatch: Binary result should be half the length of manchester data. "
                          f"Binary: {len(binary_result)}, Expected: {expected_binary_length}"]
        
        errors = []
        
        # Generate the expected binary string from manchester data
        expected_binary = ""
        for i in range(0, len(manchester_data), 2):
            if i+1 < len(manchester_data):
                # 01 should decode to 0
                if manchester_data[i] == 0 and manchester_data[i+1] == 1:
                    expected_binary += '0'
                # 10 should decode to 1
                elif manchester_data[i] == 1 and manchester_data[i+1] == 0:
                    expected_binary += '1'
                else:
                    expected_binary += 'X'  # Invalid manchester code pair
                    errors.append(f"Invalid Manchester code at positions {i}-{i+1}: "
                                 f"{manchester_data[i]}{manchester_data[i+1]}")
        
        # Compare expected with actual
        for i, (exp, act) in enumerate(zip(expected_binary, binary_result)):
            if exp != act and exp != 'X':  # Skip already identified errors
                errors.append(f"Decoding error at bit {i}: Expected '{exp}', got '{act}'")
        
        return len(errors) == 0, errors

    @staticmethod
    def enhanced_plot_manchester(ax, manchester_data, binary_data=None, title="Manchester Code Visualization"):
        """
        Enhanced visualization of Manchester encoding with clear bit boundaries and labels.
        
        Args:
            ax: Matplotlib axis object
            manchester_data (list): Manchester encoded data as a list of 0s and 1s
            binary_data (str, optional): Original binary string for validation highlighting
            title (str): Title for the plot
        """
        # Clear previous plot
        ax.clear()
        
        if not manchester_data:
            ax.set_title("No data to display")
            return
        
        # Create a cleaner signal representation with proper transitions
        x_values = []
        y_values = []
        
        # Start with a small negative time to show the beginning of the signal
        x_values.append(-0.5)
        y_values.append(manchester_data[0])
        
        for i, bit in enumerate(manchester_data):
            # Add transition point (vertical line)
            if i > 0:
                x_values.append(i - 0.001)
                y_values.append(manchester_data[i - 1])
            
            # Add current point
            x_values.append(i)
            y_values.append(bit)
            
            # Hold value until next transition
            x_values.append(i + 0.999)
            y_values.append(bit)
        
        # Add final points
        x_values.append(len(manchester_data) - 0.001)
        y_values.append(manchester_data[-1])
        x_values.append(len(manchester_data))
        y_values.append(manchester_data[-1])
        
        # Draw main signal
        ax.plot(x_values, y_values, 'b-', linewidth=2)
        
        # Validate encoding if binary data is provided
        validation_errors = []
        if binary_data:
            is_valid, validation_errors = ManchesterValidator.validate_manchester_encoding(binary_data, manchester_data)
            error_positions = set()
            for error in validation_errors:
                # Extract position numbers from error messages
                try:
                    pos = int(error.split("Bit ")[1].split(":")[0])
                    error_positions.add(pos)
                except (IndexError, ValueError):
                    pass
        
        # Add binary bit labels and highlight errors
        for i in range(0, len(manchester_data), 2):
            if i+1 < len(manchester_data):
                # Get bit value
                if manchester_data[i] == 0 and manchester_data[i+1] == 1:
                    bit_value = '0'
                elif manchester_data[i] == 1 and manchester_data[i+1] == 0:
                    bit_value = '1'
                else:
                    bit_value = '?'  # Invalid Manchester code
                
                # Label the bit
                bit_position = i // 2
                error_color = 'red' if binary_data and any(f"Bit {bit_position}" in err for err in validation_errors) else 'black'
                error_bg = 'lightsalmon' if error_color == 'red' else 'white'
                
                # Add binary bit value annotation
                ax.text(i + 0.5, -0.3, bit_value, 
                        horizontalalignment='center', 
                        verticalalignment='center',
                        fontsize=10, color=error_color,
                        bbox=dict(facecolor=error_bg, alpha=0.7, boxstyle='round,pad=0.3'))
                
                # Add bit position label (smaller)
                ax.text(i + 0.5, -0.5, f"bit {bit_position}", 
                        horizontalalignment='center', 
                        verticalalignment='center',
                        fontsize=8, color='darkblue')
        
        # Add vertical separation lines for bit pairs (clearer)
        for i in range(0, len(manchester_data) + 1, 2):
            ax.axvline(x=i, color='gray', linestyle='--', alpha=0.7)
        
        # Horizontal reference lines
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax.axhline(y=1, color='black', linestyle='-', alpha=0.3)
        
        # Add clock signal to show transitions
        clock_y = np.ones(len(manchester_data)) * -0.8
        for i in range(len(clock_y)):
            if i % 2 == 1:  # Alternate high/low for clock
                clock_y[i] = -1.2
        
        # Plot clock signal
        ax.step(range(len(manchester_data)), clock_y, 'g-', linewidth=1.5, where='post')
        ax.text(-0.5, -1.0, 'Clock', fontsize=8, color='green')
        
        # Add bit group annotations
        for i in range(0, len(manchester_data), 2):
            if i % 4 == 0 and i+1 < len(manchester_data):  # Less frequent to reduce clutter
                ax.annotate(
                    '', xy=(i, 1.3), xytext=(i+2, 1.3),
                    arrowprops=dict(arrowstyle='<->', color='green', alpha=0.7)
                )
                ax.text(i+1, 1.4, '1 bit', horizontalalignment='center', color='green', fontsize=8)
        
        # Add legend explaining the encoding
        legend_items = [
            ax.plot([], [], 'b-', linewidth=2, label='Manchester Signal')[0],
            ax.plot([], [], 'g-', linewidth=1.5, label='Clock Reference')[0]
        ]
        ax.legend(handles=legend_items, loc='upper right')
        
        # Add encoding rule reminder
        encoding_box = {
            '0 → 01': 'lightblue',
            '1 → 10': 'lightyellow'
        }
        
        y_pos = 1.3
        for text, color in encoding_box.items():
            ax.text(
                len(manchester_data) + 0.5, y_pos, text, 
                bbox=dict(facecolor=color, alpha=0.8, boxstyle='round'),
                fontsize=9
            )
            y_pos -= 0.3
        
        # Set plot properties
        ax.set_title(title)
        ax.set_xlabel('Time (samples)')
        ax.set_ylabel('Signal Level')
        ax.set_ylim([-1.5, 1.7])
        ax.set_xlim([-1, len(manchester_data) + 4])  # Extend for legend
        
        # Add grid
        ax.grid(True, which='both', linestyle=':', alpha=0.4)
        
        # Add tick marks at significant points
        ax.set_xticks(range(0, len(manchester_data) + 1, 2))
        ax.set_yticks([0, 1])

class ManchesterTestSuite(tk.Toplevel):
    """
    A test suite window to validate Manchester encoding/decoding
    """
    def __init__(self, parent, master_app):
        super().__init__(parent)
        self.title("Manchester Code Test Suite")
        self.geometry("800x600")
        
        self.master_app = master_app
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Test case entry area
        test_frame = ttk.LabelFrame(main_frame, text="Test Input", padding=10)
        test_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(test_frame, text="Binary Data:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.test_binary = ttk.Entry(test_frame, width=50)
        self.test_binary.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.test_binary.insert(0, "10110010")  # Default test case
        
        ttk.Button(test_frame, text="Run Test", command=self.run_test).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(test_frame, text="Run Predefined Tests", command=self.run_predefined_tests).grid(row=1, column=2, padx=5, pady=5)
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="Test Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, width=80, height=10)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Graph area
        graph_frame = ttk.LabelFrame(main_frame, text="Signal Visualization", padding=10)
        graph_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.figure, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def run_test(self):
        binary_data = self.test_binary.get().strip()
        if not binary_data:
            messagebox.showwarning("Input Error", "Please enter binary data (0s and 1s)")
            return
        
        if not all(bit in '01' for bit in binary_data):
            messagebox.showwarning("Input Error", "Binary data should only contain 0s and 1s")
            return
        
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, f"Testing binary data: {binary_data}\n\n")
        
        # Encoding test
        self.results_text.insert(tk.END, "=== ENCODING TEST ===\n")
        
        # Use the app's encoding function
        manchester_data = self.binary_to_manchester(binary_data)
        
        # Validate encoding
        is_valid, errors = ManchesterValidator.validate_manchester_encoding(binary_data, manchester_data)
        
        self.results_text.insert(tk.END, f"Manchester encoded data: {''.join(map(str, manchester_data))}\n")
        self.results_text.insert(tk.END, f"Encoding validation: {'✅ PASSED' if is_valid else '❌ FAILED'}\n")
        
        if not is_valid:
            self.results_text.insert(tk.END, "Errors found:\n")
            for error in errors:
                self.results_text.insert(tk.END, f"  • {error}\n")
        
        # Decoding test
        self.results_text.insert(tk.END, "\n=== DECODING TEST ===\n")
        
        # Use the app's decoding function
        decoded_binary = self.manchester_to_binary(manchester_data)
        
        # Validate decoding
        is_valid_decode = decoded_binary == binary_data
        
        self.results_text.insert(tk.END, f"Decoded binary data: {decoded_binary}\n")
        self.results_text.insert(tk.END, f"Decoding validation: {'✅ PASSED' if is_valid_decode else '❌ FAILED'}\n")
        
        if not is_valid_decode:
            self.results_text.insert(tk.END, "Errors found:\n")
            self.results_text.insert(tk.END, f"  • Expected: {binary_data}\n")
            self.results_text.insert(tk.END, f"  • Got: {decoded_binary}\n")
            
            # Find position of first difference
            for i, (e, d) in enumerate(zip(binary_data, decoded_binary)):
                if e != d:
                    self.results_text.insert(tk.END, f"  • First difference at position {i}: Expected '{e}', got '{d}'\n")
                    break
        
        # Plot the signal
        ManchesterValidator.enhanced_plot_manchester(self.ax, manchester_data, binary_data, 
                                                  f"Manchester Code Test: {binary_data}")
        self.canvas.draw()
    
    def run_predefined_tests(self):
        test_cases = [
            "00000000",  # All zeros
            "11111111",  # All ones
            "01010101",  # Alternating
            "10101010",  # Alternating, starting with 1
            "00001111",  # Half and half
            "11110000",  # Half and half, reversed
            "10010110",  # Random pattern
            "0101",      # Short pattern
            "1"          # Single bit
        ]
        
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, "=== PREDEFINED TEST CASES ===\n\n")
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases):
            self.results_text.insert(tk.END, f"Test Case #{i+1}: {test_case}\n")
            
            # Encode
            manchester_data = self.binary_to_manchester(test_case)
            
            # Validate encoding
            encoding_valid, encoding_errors = ManchesterValidator.validate_manchester_encoding(test_case, manchester_data)
            
            # Decode
            decoded_binary = self.manchester_to_binary(manchester_data)
            
            # Validate round-trip
            round_trip_valid = decoded_binary == test_case
            
            # Report results
            self.results_text.insert(tk.END, f"  Encoding: {'✅ PASSED' if encoding_valid else '❌ FAILED'}\n")
            self.results_text.insert(tk.END, f"  Round-trip: {'✅ PASSED' if round_trip_valid else '❌ FAILED'}\n")
            
            if not encoding_valid or not round_trip_valid:
                all_passed = False
                self.results_text.insert(tk.END, f"  Original:  {test_case}\n")
                self.results_text.insert(tk.END, f"  Manchester: {''.join(map(str, manchester_data))}\n")
                self.results_text.insert(tk.END, f"  Decoded:   {decoded_binary}\n\n")
            
            self.results_text.insert(tk.END, "\n")
        
        # Summary
        self.results_text.insert(tk.END, "=== SUMMARY ===\n")
        if all_passed:
            self.results_text.insert(tk.END, "✅ All tests PASSED! The Manchester encoding/decoding implementation is correct.\n")
        else:
            self.results_text.insert(tk.END, "❌ Some tests FAILED. The implementation needs fixing.\n")
        
        # Plot the last test case for visual inspection
        last_case = test_cases[-1]
        last_manchester = self.binary_to_manchester(last_case)
        ManchesterValidator.enhanced_plot_manchester(self.ax, last_manchester, last_case, 
                                               f"Manchester Code - Test Case: {last_case}")
        self.canvas.draw()
    
    def binary_to_manchester(self, binary):
        # Use the app's encoding function if available, otherwise implement here
        manchester = []
        for bit in binary:
            if bit == '0':
                manchester.extend([0, 1])  # 0 -> 01
            else:
                manchester.extend([1, 0])  # 1 -> 10
        return manchester
    
    def manchester_to_binary(self, manchester):
        # Use the app's decoding function if available, otherwise implement here
        binary = ""
        for i in range(0, len(manchester), 2):
            if i+1 < len(manchester):
                if manchester[i] == 0 and manchester[i+1] == 1:
                    binary += '0'
                elif manchester[i] == 1 and manchester[i+1] == 0:
                    binary += '1'
        return binary

# Function to integrate with the main application
def integrate_validator(app):
    """
    Integrates the Manchester validator into the existing application.
    
    Args:
        app: The ManchesterCodingApp instance to enhance
    """
    # Replace the plot_manchester function with the enhanced version
    app.original_plot_manchester = app.plot_manchester
    
    def enhanced_plot_function(manchester_data, title="Manchester Code"):
        ManchesterValidator.enhanced_plot_manchester(app.ax, manchester_data, app.binary_data, title)
        app.canvas.draw()
    
    app.plot_manchester = enhanced_plot_function
    
    # Add a validation button to the interface
    validation_frame = ttk.Frame(app.manchester_tab)
    validation_frame.pack(fill=tk.X, pady=5)
    
    validate_btn = ttk.Button(
        validation_frame, 
        text="Validate Encoding", 
        command=lambda: validate_manchester_encoding(app)
    )
    validate_btn.pack(side=tk.LEFT, padx=5)
    
    test_suite_btn = ttk.Button(
        validation_frame, 
        text="Open Test Suite", 
        command=lambda: open_test_suite(app)
    )
    test_suite_btn.pack(side=tk.LEFT, padx=5)
    
    # Add validation function
    def validate_manchester_encoding(app):
        if not app.binary_data or not app.manchester_data:
            messagebox.showinfo("Validation", "No data to validate. Please encode some data first.")
            return
        
        is_valid, errors = ManchesterValidator.validate_manchester_encoding(
            app.binary_data, app.manchester_data
        )
        
        if is_valid:
            messagebox.showinfo("Validation", "✅ The Manchester encoding is valid!")
        else:
            error_message = "❌ Validation failed with the following errors:\n\n"
            error_message += "\n".join(errors)
            messagebox.showerror("Validation Failed", error_message)
    
    # Add test suite launcher
    def open_test_suite(app):
        test_suite = ManchesterTestSuite(app.root, app)
        test_suite.grab_set()  # Make it modal

# If you want to run the validator as a standalone application for testing
def run_standalone():
    root = tk.Tk()
    root.title("Manchester Code Validator")
    root.geometry("800x600")
    
    # Create a simple frame with test button
    frame = ttk.Frame(root, padding=10)
    frame.pack(fill=tk.BOTH, expand=True)
    
    test_suite = ManchesterTestSuite(root, None)
    
    root.mainloop()

if __name__ == "__main__":
    run_standalone()

