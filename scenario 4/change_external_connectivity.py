import requests
import time
from urllib.parse import urlparse
import json

vnfd_id = 'f287e7d1-8db4-4d6b-b7d0-3f52ac887f15'
# Replace with actual API base URL and headers
BASE_URL = "http://tools.etsi.org/vnf-lcm-emulator/emulator-200/"
HEADERS = {
    "VNF-LCM-KEY": "Bearer your_access_token",
    "Version": '2.0.0',
    "Content-Type": "application/json",
    "accept": 'application/json'
}

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
        time.sleep(10)
      

def check_instance_state(vnf_instance_id):
    url = f"{BASE_URL}/vnflcm/v2/vnf_instances/{vnf_instance_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        print("instance info : ")
        res = response.json()
        state = res.get("instantiationState")
        print(res)
        print(f"instance state : {state}")
        return state
    else:
        print(f"Failed to fetch the VNF instance: {response.status_code} {response.text}")
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
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 202:
        print(f"Instantiation initiated for VNF instance {vnf_instance_id}.")
        location_header = response.headers['Location']
        parsed_url = urlparse(location_header)
        operation_id = parsed_url.path.split('/')[-1]
        return operation_id
    else:
        print(f"Failed to instantiate VNF: {response.status_code} {response.text}")


def generate_payload(instance_id):
    url = f"{BASE_URL}/vnflcm/v2/vnf_instances/{instance_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to retrieve VNF details: {response.status_code}")
        print(response.text)
        return None

    ext_virtual_links = response.json().get('instantiatedVnfInfo', {}).get('vnfVirtualLinkResourceInfo', [])

    if not ext_virtual_links:
        print("No external virtual link information found.")
        return None

    # Extract the first virtual link info as an example
    virtual_link = ext_virtual_links[0]
    virtual_link_id = virtual_link.get('id')
    resource_id = virtual_link.get('networkResource', {}).get('resourceId')

    # Example connection point (replace with dynamic logic if needed)
    cpd_id = "ext-a-left"
    ip_address = "192.168.1.100"

    payload = {
        "vnfInstanceId": instance_id,
        "extVirtualLinks": [
            {
                "id": virtual_link_id,
                "resourceId": resource_id,
                "extCps": [
                    {
                        "cpdId": cpd_id,
                        "cpProtocolData": [
                            {
                                "layerProtocol": "IPV4",
                                "ipAddresses": [
                                    {
                                        "type": "IPV4",
                                        "fixedAddresses": [ip_address]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    return payload


def change_ext_conn(instance_id):

    payload = generate_payload(instance_id)
    url = f"{BASE_URL}/vnflcm/v2/vnf_instances/{instance_id}/change_ext_conn"
    response = requests.post(url, headers=HEADERS, json= payload)
    if response.status_code == 202:
        print(f"ext connexion changing for VNF instance {instance_id}.")
        location_header = response.headers['Location']
        parsed_url = urlparse(location_header)
        operation_id = parsed_url.path.split('/')[-1]
        return operation_id
    else:
        print(f"Failed to change ext conn: {response.status_code} {response.text}")


def fetch_operation(operation_id):
    url = f"{BASE_URL}/vnflcm/v2/vnf_lcm_op_occs/{operation_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        op = response.json()
        print(f"operation: ")
        print(op)
        return op
    else:
        print(f"Failed to fetch VNFD: {response.status_code} {response.text}")
        return None


# Main Workflow
def main():
    key = 'b31bc51b-9352-4cd3-9c6d-40553c5e666c'
    print("API KEY: ",key)
    HEADERS['VNF-LCM-KEY'] = key

    vnf_instance_id = create_vnf_instance(vnfd_id, "Riad's VNF")
    time.sleep(10)

    operation_id = instantiate_vnf(vnf_instance_id)
    if check_operation_status(operation_id) != "COMPLETED":
        print("something wrong when checking operation state")
        return
    if check_instance_state(vnf_instance_id) != "INSTANTIATED": 
        print("something wrong when checking instance state")
        return
    print("Instantion of the VNF done")
    
    change_ext_conn_operation_id = change_ext_conn(vnf_instance_id)
    check_operation_status(change_ext_conn_operation_id)

    check_instance_state(vnf_instance_id)

if __name__ == "__main__":
    main()
    
    

