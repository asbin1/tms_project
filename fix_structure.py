import os
import shutil

def fix_project_structure():
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    # Check for nested trading_system
    if os.path.exists("trading_system/trading_system"):
        print("Found nested trading_system folder...")
        
        # Move files up one level if needed
        inner_dir = "trading_system/trading_system"
        for item in os.listdir(inner_dir):
            src = os.path.join(inner_dir, item)
            dst = os.path.join("trading_system", item)
            if not os.path.exists(dst):
                print(f"Moving: {item}")
                shutil.move(src, dst)
        
        # Remove empty inner folder
        if len(os.listdir(inner_dir)) == 0:
            os.rmdir(inner_dir)
    
    print("Structure fixed!")

if __name__ == "__main__":
    fix_project_structure()