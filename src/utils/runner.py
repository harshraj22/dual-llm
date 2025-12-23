import sys
import io
import traceback

def run_script(script_content: str, input_data: int) -> any:
    """
    Executes the provided python script content.
    Expects the script to define a function `solve(n)`.
    Returns the result of solve(input_data).
    """
    # Create a separate namespace for execution
    local_scope = {}
    
    # Capture stdout/stderr to prevent cluttering main output
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    captured_output = io.StringIO()
    sys.stdout = captured_output
    sys.stderr = captured_output
    
    try:
        exec(script_content, {}, local_scope)
        
        if 'solve' not in local_scope:
            return "Error: Function 'solve(n)' not defined in script."
        
        solve_func = local_scope['solve']
        try:
            result = solve_func(input_data)
            return result
        except Exception as e:
            return f"Runtime Error: {str(e)}"
            
    except Exception as e:
        return f"Syntax/Import Error: {str(e)}"
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

if __name__ == "__main__":
    code = """
def solve(n):
    return n * 2
"""
    print(run_script(code, 5))
