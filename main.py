from rich.console import Console
from rich.prompt import Prompt
import requests
from scale import main as scenario1_execute
from heal import main as scenario2_execute
from terminate import main as scenario3_execute
#from scenario2.change_external_connectivity import scenario2 as scenario2_execute




id_vnf = 'f287e7d1-8db4-4d6b-b7d0-3f52ac887f15'
# Replace with actual API base URL and headers
BASE_URL = "http://tools.etsi.org/vnf-lcm-emulator/emulator-200"
HEADERS = {
    "VNF-LCM-KEY": "Bearer your_access_token",
    "Version": '2.0.0',
    "Content-Type": "application/json",
    "accept": 'application/json'
}

# Simulation de la fonction get_apikey
def get_apikey():
    url = f"{BASE_URL}/api_key"
    response = requests.post(url, headers={'accept': 'application/json'})
    # Check if request was successful
    if response.status_code == 201:
        return response.json()  # Get API key from response JSON
    else:
        return None

# Définition des opérations avec arguments
def scenario1(key, id_vnf):
    print("\n[Scenario 1] Execution in progress...")
    scenario1_execute(key, id_vnf)  
    print("[Scenario 1] Successfully completed!")

def scenario2(key, id_vnf):
    print("\n[Scenario 2] Execution in progress...")
    scenario2_execute(key, id_vnf)  
    print("[Scenario 2] Successfully completed!")

def scenario3(key, id_vnf):
    print("\n[Scenario 3] Execution in progress...")
    scenario3_execute(key, id_vnf)  
    print("[Scenario 3] Successfully completed!")

# Main function
def main():
    console = Console()

    # Display the title
    console.print("\n[bold]Welcome to the Neva Project[/bold]", justify="center")

    # Execute get_apikey once
    key = get_apikey()
    # key = 'b31bc51b-9352-4cd3-9c6d-40553c5e666c'
    if not key:
        console.print("\n[bold red]Error: Unable to retrieve the API key.[/bold red]")
        return
    console.print(f"\n[bold]API KEY:[/bold] {key}")

    # Display the main menu
    while True:
        console.print("\n[bold]Scenarios Menu[/bold]", justify="left")
        console.print("[bold blue]1.[/bold blue] Execute Scenario 1")
        console.print("[bold blue]2.[/bold blue] Execute Scenario 2")
        console.print("[bold blue]3.[/bold blue] Execute Scenario 3")
        console.print("[bold blue]q.[/bold blue] Quit the application")

        # User choice
        choice = Prompt.ask("Please select an option", choices=["1", "2", "3", "q"])

        if choice == "q":
            console.print("\n[bold]Closing the application. Goodbye![/bold]", justify="center")
            break

        # Execute the selected Scenario with the required arguments
        console.print(f"\nYou have selected Scenario {choice}")
        scenarios[choice](key, id_vnf)

# Scenario mapping
scenarios = {
    "1": scenario1,
    "2": scenario2,
    "3": scenario3,
}

if __name__ == "__main__":
    main()
