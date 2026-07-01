# .agents/skills/sunouchi-it/scripts/fixbug_helper.py
import os
import sys
import subprocess

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "../../../.."))
    
    # Path to fix_prompt_by_erp.py
    fix_script = os.path.join(project_root, "tools/prompt_generator/fix_prompt_by_erp.py")
    
    # Path to python interpreter in venv
    venv_python = os.path.join(project_root, "venv/Scripts/python.exe")
    if not os.path.exists(venv_python):
        venv_python = "python" # fallback to system python
        
    # Forward all command line arguments
    cmd = [venv_python, fix_script] + sys.argv[1:]
    
    print(f"Running Fix Bug script: {' '.join(cmd)}")
    
    # Configure stdout/stderr to UTF-8
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    
    try:
        # Run using subprocess and inherit stdin/stdout/stderr for interactive prompt
        # We must use None for stdin/stdout/stderr to allow direct terminal interactions (stdin redirection)
        res = subprocess.run(cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
        sys.exit(res.returncode)
    except Exception as e:
        print(f"Error executing fixbug: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
