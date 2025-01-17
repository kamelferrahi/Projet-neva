import requests
import time
from urllib.parse import urlparse


id_vnf = 'f287e7d1-8db4-4d6b-b7d0-3f52ac887f15'
# Replace with actual API base URL and headers
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
        "flavourId": "df-normal",  
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


# Main Workflow
def main():

    #key = get_apikey()
    key = 'aaf0e8f9-29f7-4f57-97e9-65c0dc9a9990'
    print("API KEY: ",key)
    HEADERS['VNF-LCM-KEY'] = key

    vnf_instance_id = create_vnf_instance(id_vnf, 'First_VNFD')

    operation_id = instantiate_vnf(vnf_instance_id)
    if check_operation_status(operation_id) != "COMPLETED":
        return
    
    print("First Instantion of the VNF done")
    print("Initiating the termination of the VNF")
    # Terminate the VNF
    operation_id = terminate_vnf(vnf_instance_id)
    if not operation_id:
        return
    
    # Check termination status
    if check_operation_status(operation_id) != "COMPLETED":
        return
    
    print("VNF Terminated")
    # Fetch VNFD
    vnfd_id = fetch_vnfd(vnf_instance_id)
    if not vnfd_id:
        return
    
    # Create a new VNF instance
    new_vnf_instance_id = create_vnf_instance(id_vnf, "Second_VNFD")
    if not new_vnf_instance_id:
        return
    
    # Instantiate the new VNF
    print("Initiating the reinstantion of the VNF")
    operation_id = instantiate_vnf(new_vnf_instance_id)

    if not operation_id:
        return

    if check_operation_status(operation_id) != "COMPLETED":
        return
    
    print("VNF reinstantion with success")

if __name__ == "__main__":
    main()
    
    

