import csv
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.storage import StorageManagementClient
import pandas as pd

# Initialize Azure clients
credential = DefaultAzureCredential()
subscription_id = "<YOUR_SUBSCRIPTION_ID>"

resource_client = ResourceManagementClient(credential, subscription_id)
compute_client = ComputeManagementClient(credential, subscription_id)
storage_client = StorageManagementClient(credential, subscription_id)

# Data to store disk and storage account information
disk_data = []
storage_account_data = []

# Fetch resource groups
resource_groups = resource_client.resource_groups.list()

# Fetch disks and storage accounts for each resource group
for rg in resource_groups:
    resource_group_name = rg.name

    # Fetch disks (OS and data disks)
    disks = compute_client.disks.list_by_resource_group(resource_group_name)
    for disk in disks:
        disk_data.append({
            "Resource Group": resource_group_name,
            "Disk Name": disk.name,
            "Disk Type": disk.sku.name if disk.sku else "Unknown",
            "Disk Size (GB)": disk.disk_size_gb,
            "Attached To": disk.managed_by if disk.managed_by else "Not Attached",
            "Disk State": disk.provisioning_state,  # Corrected attribute
            "Tags": disk.tags
        })

    # Fetch storage accounts
    storage_accounts = storage_client.storage_accounts.list_by_resource_group(resource_group_name)
    for sa in storage_accounts:
        storage_account = storage_client.storage_accounts.get_properties(resource_group_name, sa.name)
        storage_account_data.append({
            "Resource Group": resource_group_name,
            "Storage Account Name": sa.name,
            "Storage Type": storage_account.sku.name,
            "Access Tier": storage_account.access_tier if hasattr(storage_account, "access_tier") else "N/A",
            "Location": storage_account.location,
            "Kind": storage_account.kind,
            "Tags": sa.tags
        })

# Export disk data to CSV
disk_df = pd.DataFrame(disk_data)
disk_df.to_csv("azure_disks.csv", index=False)
print("Disk information exported to azure_disks.csv")

# Export storage account data to CSV
storage_account_df = pd.DataFrame(storage_account_data)
storage_account_df.to_csv("azure_storage_accounts.csv", index=False)
print("Storage account information exported to azure_storage_accounts.csv")
