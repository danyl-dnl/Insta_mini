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
    "owner_id": 1,  # Owner ID 1 corresponds to alice
    "caption": "Enjoying coding with Antigravity!"
}

def check_permission(user: dict, action: str, post: dict = None) -> bool:
    user_role = user.get("role")
    permissions = ROLE_PERMISSIONS.get(user_role)
    if action=="delete_own_post" and "delete_any_post" in permissions:
        return True
    elif action=="delete_own_post" and post.get("owner_id") == user.get("user_id"):
        return True
    else:
        return False
        
        





result = check_permission(users["alex"],"delete_own_post", test_post)

if result:
    print("Yes its possible ")
else:
    print("no its not possible")
