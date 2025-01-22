import requests
import time
from urllib.parse import urlparse
import json

#id_vnf = 'f287e7d1-8db4-4d6b-b7d0-3f52ac887f15'
# Replace with actual API base URL and headers
BASE_URL = "http://tools.etsi.org/vnf-lcm-emulator/emulator-200"
HEADERS = {
    "VNF-LCM-KEY": "Bearer your_access_token",
    "Version": '2.0.0',
    "Content-Type": "application/json",
    "accept": 'application/json'
}

def get_apikey():
    url = f"{BASE_URL}/api_key"
    response = requests.post(url, headers={'accept': 'application/json'})
    # Check if request was successful
    if response.status_code == 201:
        return response.json()  # Get API key from response JSON
    else:
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

def heal_vnf(vnf_instance_id, cause):
    url = f"{BASE_URL}/vnflcm/v2/vnf_instances/{vnf_instance_id}/heal"
    payload = {
        "additionalParams": {},
        "cause": cause
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 202:
        location_header = response.headers['Location']
        parsed_url = urlparse(location_header)
        operation_id = parsed_url.path.split('/')[-1]
        print(f"Healing initiated : Operation ID: {operation_id}")
        return operation_id
    else:
        print(f"Failed to heal VNF: {response.status_code} {response.text}")
        return None
""""" 
def operate_vnf(vnf_instance_id, stateto):
    url = f"{BASE_URL}/vnflcm/v2/vnf_instances/{vnf_instance_id}/operate"
    payload = {
        "additionalParams": {},
        "changeStateTo": stateto,
        "gracefulStopTimeout": 0,
        "stopType": "FORCEFUL"
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 202:
        location_header = response.headers['Location']
        parsed_url = urlparse(location_header)
        operation_id = parsed_url.path.split('/')[-1]
        print(f"Changing the state : Operation ID: {operation_id}")
        return operation_id
    else:
        print(f"Failed to change the VNF's state : {response.status_code} {response.text}")
        return None
"""
def format_vnf_info(data):
    formatted_data = {
        "VNF Instance": {
            "ID": data.get("id"),
            "Name": data.get("vnfInstanceName"),
            "Description": data.get("vnfInstanceDescription"),
            "State": data.get("instantiationState"),
            "VNF State": data.get("instantiatedVnfInfo", {}).get("vnfState"),
            "Provider": data.get("vnfProvider"),
            "Software Version": data.get("vnfSoftwareVersion"),
            "VNFD ID": data.get("vnfdId"),
            "VNFD Version": data.get("vnfdVersion"),
            "Configurable Properties": data.get("vnfConfigurableProperties"),
        },
        "Links": data.get("_links", {}),
        "Instantiated Info": {
            "Flavor ID": data.get("instantiatedVnfInfo", {}).get("flavourId"),
            "Scale Status": data.get("instantiatedVnfInfo", {}).get("scaleStatus"),
            "Max Scale Levels": data.get("instantiatedVnfInfo", {}).get("maxScaleLevels"),
            "Virtual Storage": [
                {
                    "Storage ID": storage.get("id"),
                    "Resource ID": storage.get("storageResource", {}).get("resourceId"),
                    "Desc ID": storage.get("virtualStorageDescId"),
                }
                for storage in data.get("instantiatedVnfInfo", {}).get("virtualStorageResourceInfo", [])
            ],
            "Virtual Link Info": [
                {
                    "Link ID": link.get("id"),
                    "Resource ID": link.get("networkResource", {}).get("resourceId"),
                    "Desc ID": link.get("vnfVirtualLinkDescId"),
                }
                for link in data.get("instantiatedVnfInfo", {}).get("vnfVirtualLinkResourceInfo", [])
            ],
            "VNFC Resource Info": [
                {
                    "VNFC ID": vnfc.get("id"),
                    "Compute Resource ID": vnfc.get("computeResource", {}).get("resourceId"),
                    "Storage Resource IDs": vnfc.get("storageResourceIds"),
                    "VDU ID": vnfc.get("vduId"),
                    "CP Info": [
                        {
                            "CP ID": cp.get("id"),
                            "CPD ID": cp.get("cpdId"),
                            "MAC Address": cp.get("cpProtocolInfo", [{}])[0]
                            .get("ipOverEthernet", {})
                            .get("macAddress"),
                        }
                        for cp in vnfc.get("vnfcCpInfo", [])
                    ],
                }
                for vnfc in data.get("instantiatedVnfInfo", {}).get("vnfcResourceInfo", [])
            ],
        },
    }
    return json.dumps(formatted_data, indent=4)
    
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
      

def check_instance_state(vnf_instance_id):
    url = f"{BASE_URL}/vnflcm/v2/vnf_instances/{vnf_instance_id}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        print("instance info : ")
        res = response.json()
        print(format_vnf_info(res))
        state = res.get("instantiationState")
        #print(res)
        print(f"instance state : {state}")
        return state
    else:
        print(f"Failed to fetch the VNF instance: {response.status_code} {response.text}")
        return None

def scenario2(key, id_vnf):
    #key = get_apikey()
    #key = 'b31bc51b-9352-4cd3-9c6d-40553c5e666c'
    print("API KEY: ", key)
    HEADERS['VNF-LCM-KEY'] = key
    
    # Create and instantiate the first VNF instance
    vnf_instance_id = create_vnf_instance(id_vnf, 'First_VNFD')
    operation_id = instantiate_vnf(vnf_instance_id)
    if check_operation_status(operation_id) != "COMPLETED":
        return
    
    print("Instantiation of the VNF done")
    
    
    print("Healing vnf started")
    # Heal the VNF
    operation_id = heal_vnf(vnf_instance_id, cause="Memory overflow")
    if not operation_id:
        return
    
    # Check healing status
    if check_operation_status(operation_id) != "COMPLETED":
        return
    
    print("Healing completed successfully")
    
    check_instance_state(vnf_instance_id)

    
if __name__ == "__main__":
    key = 'b31bc51b-9352-4cd3-9c6d-40553c5e666c'
    id_vnf = 'f287e7d1-8db4-4d6b-b7d0-3f52ac887f15'
    scenario2(key, id_vnf)
    
    