import os

def remove_terraform_files(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".terraform") or file.endswith(".terraform.lock.hcl"):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Arquivo removido: {file_path}")

        for dir in dirs:
            if dir == ".terraform":
                dir_path = os.path.join(root, dir)
                os.system(f"rm -rf {dir_path}")
                print(f"Pasta removida: {dir_path}")

if __name__ == "__main__":
    current_dir = os.getcwd()
    remove_terraform_files(current_dir)
