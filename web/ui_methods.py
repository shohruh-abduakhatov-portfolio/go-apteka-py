def has_access(self, roles):
    user = self.current_user
    """
    user_roles = user["roles"]
    has_access = False
    for role in user_roles:
        if _checkRole(role, roles) == True:
            has_access = True
            break
    return has_access
    
    """
    return True

def _checkRole(role, roles):
    ''' Check given role is inside or equals to roles '''
    # Roles is a list not a single element
    if isinstance(roles, list):
        found = False
        for r in roles:
            if r.value == role["value"]:
                found = True
                break
 
        if found == True:
            return True
 
    # Role is a single string
    else:
        if roles.value == role:
            return True
 
    return False
