from core.gns3_manager import GNS3Manager


gns3 = GNS3Manager()

result = gns3.test_connection()

print("=" * 50)
print("KIEM TRA GNS3")
print("=" * 50)

if result["success"]:

    print("[OK] Ket noi GNS3 thanh cong")
    print(result["data"])

else:

    print("[ERROR] Khong ket noi duoc GNS3")
    print(result["error"])