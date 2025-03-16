from .models import CabinetModel, UserCabinetStatus

def get_cabinet_from_path(path):
    # Resolve cabinet hierarchy from URL path
    if not path:
        return None
    
    current = None
    for name in path.split('/'):
        try:
            current = CabinetModel.objects.get(
                name=name, 
                parent=current if current else None
            )
        except CabinetModel.DoesNotExist:
            return None
    return current

def validate_cabinet_access(user, cabinet):
    # Check if user can access cabinet
    if not cabinet.requires_questions:
        return True
        
    if not user.is_authenticated:
        return False
        
    status = UserCabinetStatus.objects.filter(
        user=user, 
        cabinet=cabinet
    ).first()
    
    return not (status and status.locked)