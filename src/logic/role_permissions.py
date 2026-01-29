# src/logic/role_permissions.py
"""
Role-based permission logic
Defines what each role can and cannot do (logic only, no UI)
"""

from typing import Dict, List, Optional, Any
from enum import Enum


class UserRole(Enum):
    """User role enumeration"""
    ETUDIANT = "etudiant"
    ENSEIGNANT = "enseignant"
    ADMIN = "admin"


class RolePermissions:
    """Role-based permission checker (logic only)"""
    
    @staticmethod
    def can_view_group_timetable(user_role: str, user_groupe_id: Optional[int],
                                 requested_groupe_id: Optional[int]) -> bool:
        """
        Check if user can view a group's timetable
        - Etudiant: can ONLY view their own group
        - Enseignant: can view any group (for their sessions)
        - Admin: can view any group
        """
        if user_role == UserRole.ETUDIANT.value:
            # Students can only view their own group
            return user_groupe_id is not None and user_groupe_id == requested_groupe_id
        elif user_role == UserRole.ENSEIGNANT.value:
            # Teachers can view groups they teach
            return True
        elif user_role == UserRole.ADMIN.value:
            # Admins can view all groups
            return True
        return False
    
    @staticmethod
    def can_view_rooms(user_role: str) -> bool:
        """
        Check if user can view available rooms
        - All roles can view rooms
        """
        return True
    
    @staticmethod
    def can_create_reservation(user_role: str) -> bool:
        """
        Check if user can create a reservation request
        - Etudiant: CANNOT create reservations
        - Enseignant: CAN create reservations
        - Admin: CAN create reservations (but typically don't)
        """
        if user_role == UserRole.ETUDIANT.value:
            return False
        elif user_role == UserRole.ENSEIGNANT.value:
            return True
        elif user_role == UserRole.ADMIN.value:
            return True  # Admin can, but typically won't
        return False
    
    @staticmethod
    def can_view_personal_timetable(user_role: str) -> bool:
        """
        Check if user can view their personal timetable
        - Etudiant: can view their group timetable
        - Enseignant: can view their teaching schedule
        - Admin: can view any timetable
        """
        return True
    
    @staticmethod
    def can_declare_unavailability(user_role: str) -> bool:
        """
        Check if user can declare unavailability
        - Etudiant: CANNOT
        - Enseignant: CAN
        - Admin: CAN (but typically don't)
        """
        if user_role == UserRole.ETUDIANT.value:
            return False
        elif user_role == UserRole.ENSEIGNANT.value:
            return True
        elif user_role == UserRole.ADMIN.value:
            return True
        return False
    
    @staticmethod
    def can_approve_reservations(user_role: str) -> bool:
        """
        Check if user can approve/reject reservations
        - Only Admin can approve reservations
        """
        return user_role == UserRole.ADMIN.value
    
    @staticmethod
    def can_generate_timetables(user_role: str) -> bool:
        """
        Check if user can generate timetables automatically
        - Only Admin can generate timetables
        """
        return user_role == UserRole.ADMIN.value
    
    @staticmethod
    def can_view_all_reservations(user_role: str) -> bool:
        """
        Check if user can view all reservation requests
        - Only Admin can view all requests
        - Enseignant can view their own requests
        """
        return user_role == UserRole.ADMIN.value
    
    @staticmethod
    def can_view_own_reservations(user_role: str) -> bool:
        """
        Check if user can view their own reservation requests
        - Enseignant: can view their own requests
        - Admin: can view all requests
        """
        return user_role in [UserRole.ENSEIGNANT.value, UserRole.ADMIN.value]
    
    @staticmethod
    def filter_reservations_by_permission(user_role: str, user_id: Optional[int],
                                         all_reservations: List[Dict]) -> List[Dict]:
        """
        Filter reservations based on user permissions
        - Etudiant: no reservations
        - Enseignant: only their own reservations
        - Admin: all reservations
        """
        if user_role == UserRole.ETUDIANT.value:
            return []
        elif user_role == UserRole.ENSEIGNANT.value:
            if user_id is None:
                return []
            return [r for r in all_reservations if r.get('enseignant_id') == user_id]
        elif user_role == UserRole.ADMIN.value:
            return all_reservations
        return []
    
    @staticmethod
    def filter_seances_by_permission(user_role: str, user_id: Optional[int],
                                    user_groupe_id: Optional[int],
                                    all_seances: List[Dict]) -> List[Dict]:
        """
        Filter sessions based on user permissions
        - Etudiant: only sessions of their group
        - Enseignant: only their own sessions
        - Admin: all sessions
        """
        if user_role == UserRole.ETUDIANT.value:
            if user_groupe_id is None:
                return []
            return [s for s in all_seances if s.get('groupe_id') == user_groupe_id]
        elif user_role == UserRole.ENSEIGNANT.value:
            if user_id is None:
                return []
            return [s for s in all_seances if s.get('enseignant_id') == user_id]
        elif user_role == UserRole.ADMIN.value:
            return all_seances
        return []