import subprocess
import pkg_resources
import tempfile
import shutil
from pathlib import Path

class ToolInstaller:
    def __init__(self, ai_model):
        self.ai_model = ai_model
        self.installed_tools = {}
        
    def install_tool_dynamically(self, target_os, tool_name):
        """Install security tools based on AI recommendations."""
        params = self.ai_model.get_install_params(tool_name, target_os)
        
        if tool_name in self.installed_tools:
            return self.installed_tools[tool_name]
            
        if params.get("install_method") == "package_manager":
            return self._install_via_package_manager(tool_name, params)
        elif params.get("install_method") == "source":
            return self._install_from_source(tool_name, params)
        elif params.get("install_method") == "docker":
            return self._install_via_docker(tool_name, params)
            
    def _install_via_package_manager(self, tool_name, params):
        cmd = [
            "sudo", params.get("package_manager"), "install",
            "-y", tool_name
        ]
        subprocess.run(cmd, check=True)
        self.installed_tools[tool_name] = params.get("path")
        return params.get("path")
        
    def _install_from_source(self, tool_name, params):
        temp_dir = tempfile.mkdtemp()
        try:
            subprocess.run([
                "git", "clone", params.get("repo_url"), temp_dir
            ], check=True)
            
            subprocess.run([
                "./configure", "--prefix", params.get("install_path")
            ], cwd=temp_dir, check=True)
            
            subprocess.run(["make"], cwd=temp_dir, check=True)
            subprocess.run(["make", "install"], cwd=temp_dir, check=True)
            
            self.installed_tools[tool_name] = params.get("install_path")
            return params.get("install_path")
        finally:
            shutil.rmtree(temp_dir)
            
    def _install_via_docker(self, tool_name, params):
        container_id = subprocess.check_output([
            "docker", "run", "-d", params.get("image_name")
        ]).decode().strip()
        
        dest_path = Path(params.get("host_path")) / tool_name
        subprocess.run([
            "docker", "cp", f"{container_id}:/usr/local/bin/{tool_name}", dest_path
        ], check=True)
        
        subprocess.run(["docker", "rm", container_id], check=True)
        self.installed_tools[tool_name] = str(dest_path)
        return str(dest_path)
