import subprocess
import sys

def sign_image(payload: str, signing_key: str):
    cosign_command = f"cd /root/HSM_DPOD && source ./setenv && cosign sign --key \"{signing_key}\" {payload}"
    input_cmd_list = []
    input_cmd_list.append(cosign_command)
    # execute the cosign_command
    try:
        result = subprocess.run(
                input_cmd_list,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
    except subprocess.TimeoutExpired:
        print("the command took too long to complete")
    except subprocess.CalledProcessError as e:
        print(f"the subrocess encountered an error while running the command {str(e)}")
    print(f"{result.stdout} {result.stderr}")

def main():
    sign_image(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
