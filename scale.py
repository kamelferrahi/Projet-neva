import requests
import time
from urllib.parse import urlparse
from rich.console import Console
from rich.prompt import Prompt
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console = Console()


BASE_URL = "http://tools.etsi.org/vnf-lcm-emulator/emulator-200/"
HEADERS = {
    "VNF-LCM-KEY": "Bearer your_access_token",
    "Version": '2.0.0',
    "Content-Type": "application/json",
    "accept": 'application/json'
}

def get_apikey():
    u = url = f"{BASE_URL}/api_key"
    response = requests.post(url)
    return response.json()

def terminate_vnf(vnf_instance_id):
    url = f"{BASE_URL}/vnflcm/v2/vnf_instances/{vnf_instance_id}/terminate"
    payload = {
        "additionalParams": {},
        "terminationType": "FORCEFUL",
        "gracefulTerminationTimeout": 0,
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 202:
        location_header = response.headers['Location']
        parsed_url = urlparse(location_header)
        operation_id = parsed_url.path.split('/')[-1]
        print(f"Termination initiated. Operation ID: {operation_id}")
        return operation_id
    else:
        print(f"Failed to initiate termination: {response.status_code} {response.text}")
        return None

def check_operation_status(operation_id):
    url = f"{BASE_URL}/vnflcm/v2/vnf_lcm_op_occs/{operation_id}"
    last_status = None
    while True:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            operation_status = response.json().get("operationState")
            if (operation_status != last_status):
                print(f"Current operation status: {operation_status}")
            if operation_status in ["COMPLETED", "FAILED"]:
                return operation_status
        else:
            print(f"Failed to check status: {response.status_code} {response.text}")
            return None
        last_status = operation_status
      

def fetch_vnfd(vnf_instance_id):
    url = f"{BASE_URL}/vnflcm/v2/vnf_instances/{vnf_instance_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        vnfd_id = response.json().get("vnfdId")
        print(f"VNFD ID fetched: {vnfd_id}")
        return vnfd_id
    else:
        print(f"Failed to fetch VNFD: {response.status_code} {response.text}")
        return None

def create_vnf_instance(vnfd_id, name):
    url = f"{BASE_URL}/vnflcm/v2/vnf_instances"
    payload = {
       'metadata': {},
        "vnfdId": vnfd_id,
        "vnfInstanceName": name,
        "vnfInstanceDescription": 'VNF simulation'
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 201:
        vnf_instance_id = response.json().get("id")
        print(f"New VNF instance created. Instance ID: {vnf_instance_id}")
        return vnf_instance_id
    else:
        print(f"Failed to create VNF instance: {response.status_code} {response.text}")
        return None

def instantiate_vnf(vnf_instance_id):
    url = f"{BASE_URL}/vnflcm/v2/vnf_instances/{vnf_instance_id}/instantiate"
    payload = {
        "flavourId": "df-big",  
    }
    response = requests.post(url, headers=HEADERS, json= payload)
    if response.status_code == 202:
        print(f"Instantiation initiated for VNF instance {vnf_instance_id}.")
        location_header = response.headers['Location']
        parsed_url = urlparse(location_header)
        operation_id = parsed_url.path.split('/')[-1]
        return operation_id
    else:
        print(f"Failed to instantiate VNF: {response.status_code} {response.text}")


def fetch_operation(operation_id):
    url = f"{BASE_URL}/vnflcm/v2/vnf_lcm_op_occs/{operation_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        vnfd_id = response.json()
        print(f"operations: {vnfd_id}")
        return vnfd_id
    else:
        print(f"Failed to fetch VNFD: {response.status_code} {response.text}")
        return None

def scale_to_level(vnf_instance_id, aspect_id, scale_level, vnfd_id):
    url = f"{BASE_URL}/vnflcm/v2/vnf_instances/{vnf_instance_id}/scale_to_level"
    payload = {
        "scaleInfo": [
            {
                "aspectId": aspect_id,
                "scaleLevel": scale_level,
                "vnfdId": vnfd_id
            }
        ]
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 202:
        print(f"Scaling operation initiated for VNF instance {vnf_instance_id}.")
        location_header = response.headers['Location']
        parsed_url = urlparse(location_header)
        operation_id = parsed_url.path.split('/')[-1]
        return operation_id
    else:
        print(f"Failed to scale VNF: {response.status_code} {response.text}")
        return None

def scale_vnf(vnf_instance_id, aspect_id, number_of_steps, scale_type):

    url = f"{BASE_URL}/vnflcm/v2/vnf_instances/{vnf_instance_id}/scale"
    payload = {
        "aspectId": aspect_id,
        "numberOfSteps": number_of_steps,
        "type": scale_type
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 202:
        print(f"Scaling operation initiated for VNF instance {vnf_instance_id}.")
        location_header = response.headers['Location']
        parsed_url = urlparse(location_header)
        operation_id = parsed_url.path.split('/')[-1]
        return operation_id
    else:
        print(f"Failed to scale VNF: {response.status_code} {response.text}")
        return None


def main(key, id_vnf):
    """
    Main workflow for simulating scaling operations on a virtual network function (VNF).
    """
    # Set the VNF LCM Key header
    HEADERS['VNF-LCM-KEY'] = key
    aspect_id = "big"
    scale_level = 1
    number_of_steps = 1
    scale_type = "SCALE_OUT"

    console.print("Objective: Simulate scaling operations to modify the capacity of a Virtual Network Function (VNF).", style="blue")

    # Step 1: Create a VNF Instance
    console.print("\nStep 1: Creating a VNF Instance", style="blue")
    vnf_instance_id = create_vnf_instance(id_vnf, 'First_VNFD')
    if not vnf_instance_id:
        logging.error("Failed to create VNF instance.")
        return

    operation_id = instantiate_vnf(vnf_instance_id)
    if check_operation_status(operation_id) != "COMPLETED":
        logging.error("VNF instantiation failed.")
        return
    console.print("VNF instantiation completed successfully.", style="blue")

    # Step 2: Fetch VNFD
    vnfd_id = fetch_vnfd(vnf_instance_id)
    if not vnfd_id:
        logging.error("Failed to fetch VNFD for the VNF instance.")
        return

    # Step 3: Scale VNF
    console.print("\nStep 2: Scaling VNF", style="blue")
    while True:
        console.print("\nSelect an operation:")
        console.print("1. Scale to a specific level")
        console.print("2. Perform scaling operation")
        console.print("q. Quit the scaling scenario")

        choice = Prompt.ask("Please select an option", choices=["1", "2", "q"])
        if choice == "1":
            # Scale to a specific level
            console.print("Initiating scale-to-level operation...", style="blue")
            operation_id = scale_to_level(vnf_instance_id, aspect_id, scale_level, id_vnf)
            if not operation_id:
                logging.error("Failed to initiate scale-to-level operation.")
                return
            console.print("Step 3: Checking Scaling Status", style="blue")
            if check_operation_status(operation_id) == "COMPLETED":
                console.print(f"VNF instance {vnf_instance_id} successfully scaled to level {scale_level}.", style="blue")
            else:
                logging.error(f"Scaling to level operation for VNF instance {vnf_instance_id} failed.")
        elif choice == "2":
            # Perform scaling operation
            console.print("Initiating scaling operation...", style="blue")
            operation_id = scale_vnf(vnf_instance_id, aspect_id, number_of_steps, scale_type)
            if not operation_id:
                logging.error("Failed to initiate scaling operation.")
                return
            console.print("Step 3: Checking Scaling Status", style="blue")
            if check_operation_status(operation_id) == "COMPLETED":
                console.print(f"VNF instance {vnf_instance_id} successfully scaled with aspect {aspect_id}.", style="blue")
            else:
                logging.error(f"Scaling operation for VNF instance {vnf_instance_id} failed.")
        elif choice == "q":
            console.print("Exiting the scaling scenario.", style="blue")
            break


if __name__ == "__main__":
    # Example credentials
    key = 'b31bc51b-9352-4cd3-9c6d-40553c5e666c'
    id_vnf = 'f287e7d1-8db4-4d6b-b7d0-3f52ac887f15'
    main(key, id_vnf)
   