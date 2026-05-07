from typing import Tuple, List, Dict, Optional
from core.adb_manager import ADBManager
from utils.logger import Logger
from utils.colors import Colors


class PermissionManager:

    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None):
        self.adb = adb_manager
        self.logger = logger

    def list_permissions(self, package_name: str) -> Tuple[bool, Dict[str, List[str]]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🔐 Package Permissions                         ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, {}

        if not package_name:
            print(f"{Colors.FAIL}❌ Package name is required{Colors.ENDC}")
            return False, {}

        print(f"{Colors.OKBLUE}📦 Package: {package_name}{Colors.ENDC}\n")

        result = self.adb.shell_command(f'dumpsys package {package_name}')

        if not result.success or not result.output:
            print(f"{Colors.FAIL}❌ Failed to get permissions{Colors.ENDC}")
            return False, {}

        granted = []
        denied = []

        lines = result.output.split('\n')
        in_permissions = False

        for line in lines:
            if 'requested permissions:' in line.lower():
                in_permissions = True
                continue

            if in_permissions:
                if line.strip().startswith('android.permission.'):
                    perm = line.strip().split(':')[0]
                    if ': granted=true' in line:
                        granted.append(perm)
                    else:
                        denied.append(perm)
                elif not line.strip() or 'install permissions:' in line.lower():
                    break

        permissions = {'granted': granted, 'denied': denied}

        print(f"{Colors.OKGREEN}✅ Granted permissions ({len(granted)}):{Colors.ENDC}")
        for perm in granted:
            print(f"{Colors.OKGREEN}   ✓ {perm}{Colors.ENDC}")

        if denied:
            print(f"\n{Colors.WARNING}❌ Denied permissions ({len(denied)}):{Colors.ENDC}")
            for perm in denied:
                print(f"{Colors.WARNING}   ✗ {perm}{Colors.ENDC}")

        print()

        if self.logger:
            self.logger.log_event('list_permissions', f'{package_name}: {len(granted)} granted, {len(denied)} denied')

        return True, permissions

    def grant_permission(self, package_name: str, permission: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ✅ Grant Permission                            ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        if not package_name or not permission:
            print(f"{Colors.FAIL}❌ Package name and permission are required{Colors.ENDC}")
            return False, "Package name and permission are required"

        print(f"{Colors.OKBLUE}📦 Package: {package_name}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}🔐 Permission: {permission}{Colors.ENDC}\n")

        result = self.adb.shell_command(f'pm grant {package_name} {permission}')

        if result.success:
            print(f"{Colors.OKGREEN}✅ Permission granted{Colors.ENDC}\n")

            if self.logger:
                self.logger.log_event('grant_permission', f'{package_name}: {permission}')

            return True, f"Permission {permission} granted to {package_name}"
        else:
            print(f"{Colors.FAIL}❌ Failed to grant permission{Colors.ENDC}")
            return False, "Failed to grant permission"

    def revoke_permission(self, package_name: str, permission: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ❌ Revoke Permission                           ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        if not package_name or not permission:
            print(f"{Colors.FAIL}❌ Package name and permission are required{Colors.ENDC}")
            return False, "Package name and permission are required"

        print(f"{Colors.OKBLUE}📦 Package: {package_name}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}🔐 Permission: {permission}{Colors.ENDC}\n")

        result = self.adb.shell_command(f'pm revoke {package_name} {permission}')

        if result.success:
            print(f"{Colors.OKGREEN}✅ Permission revoked{Colors.ENDC}\n")

            if self.logger:
                self.logger.log_event('revoke_permission', f'{package_name}: {permission}')

            return True, f"Permission {permission} revoked from {package_name}"
        else:
            print(f"{Colors.FAIL}❌ Failed to revoke permission{Colors.ENDC}")
            return False, "Failed to revoke permission"

    def batch_grant_permissions(self, package_name: str, permissions: List[str]) -> Tuple[bool, int, int]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ✅ Batch Grant Permissions                     ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, 0, 0

        print(f"{Colors.OKBLUE}📦 Package: {package_name}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}🔐 Granting {len(permissions)} permission(s)...{Colors.ENDC}\n")

        granted = 0
        failed = 0

        for perm in permissions:
            result = self.adb.shell_command(f'pm grant {package_name} {perm}')
            if result.success:
                granted += 1
                print(f"{Colors.OKGREEN}   ✓ {perm}{Colors.ENDC}")
            else:
                failed += 1
                print(f"{Colors.FAIL}   ✗ {perm}{Colors.ENDC}")

        print(f"\n{Colors.OKGREEN}✅ Granted: {granted}{Colors.ENDC}")
        if failed > 0:
            print(f"{Colors.FAIL}❌ Failed: {failed}{Colors.ENDC}")
        print()

        if self.logger:
            self.logger.log_event('batch_grant_permissions', f'{package_name}: {granted} granted, {failed} failed')

        return True, granted, failed

    def batch_revoke_permissions(self, package_name: str, permissions: List[str]) -> Tuple[bool, int, int]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ❌ Batch Revoke Permissions                    ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, 0, 0

        print(f"{Colors.OKBLUE}📦 Package: {package_name}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}🔐 Revoking {len(permissions)} permission(s)...{Colors.ENDC}\n")

        revoked = 0
        failed = 0

        for perm in permissions:
            result = self.adb.shell_command(f'pm revoke {package_name} {perm}')
            if result.success:
                revoked += 1
                print(f"{Colors.OKGREEN}   ✓ {perm}{Colors.ENDC}")
            else:
                failed += 1
                print(f"{Colors.FAIL}   ✗ {perm}{Colors.ENDC}")

        print(f"\n{Colors.OKGREEN}✅ Revoked: {revoked}{Colors.ENDC}")
        if failed > 0:
            print(f"{Colors.FAIL}❌ Failed: {failed}{Colors.ENDC}")
        print()

        if self.logger:
            self.logger.log_event('batch_revoke_permissions', f'{package_name}: {revoked} revoked, {failed} failed')

        return True, revoked, failed

    def close(self):
        pass


def create_permission_manager(adb_manager: ADBManager, logger: Optional[Logger] = None) -> PermissionManager:
    return PermissionManager(adb_manager, logger)


def get_default_permission_manager(adb_manager: ADBManager) -> PermissionManager:
    from utils.logger import get_default_logger
    return PermissionManager(adb_manager, get_default_logger())
