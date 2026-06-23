ROLE_PERMISSIONS = {
    "User": ["create_post", "delete_own_post"],
    "Supervisor": ["create_post", "delete_own_post", "delete_any_post"],
    "Admin":["create_post", "delete_own_post", "delete_any_post", "delete_user"],
    "SuperAdmin": ["create_post", "delete_own_post", "delete_any_post", "delete_user", "assign_roles"]
}

users = {
    "alice": {"user_id": 1, "username": "alice", "role": "User"},
    "bob": {"user_id": 2, "username": "bob", "role": "User"},
    "sam": {"user_id": 3, "username": "sam", "role": "Supervisor"},
    "alex": {"user_id": 4, "username": "alex", "role": "Admin"},
    "super_owner": {"user_id": 5, "username": "super_owner", "role": "SuperAdmin"},
}

test_post = {
    "post_id": 101,
    "owner_id": 1,  
    "caption": "Enjoying coding"
}

def check_permission(user: dict, action: str, post: dict = None) -> bool:
    user_role = user.get("role")
    permissions = ROLE_PERMISSIONS.get(user_role, [])

    if action == "delete_own_post":
        if "delete_any_post" in permissions:
            return True
        if "delete_own_post" in permissions and post.get("owner_id") == user.get("user_id"):
            return True
        return False

    elif action in permissions:
        return True
    else:
        return False





print("1. Alice deleting her own post (Expected: Yes):")
print("Yes" if check_permission(users["alice"], "delete_own_post", test_post) else "No")

print("\n2. Bob deleting Alice's post (Expected: No):")
print("Yes" if check_permission(users["bob"], "delete_own_post", test_post) else "No")

print("\n3. Supervisor Sam deleting Alice's post (Expected: Yes):")
print("Yes" if check_permission(users["sam"], "delete_own_post", test_post) else "No")

print("\n4. Alice creating a post (Expected: Yes):")
print("Yes" if check_permission(users["alice"], "create_post") else "No")

print("\n5. Admin Alex deleting a user (Expected: Yes):")
print("Yes" if check_permission(users["alex"], "delete_user") else "No")
