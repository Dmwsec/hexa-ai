import asyncio
import aiohttp
from ai_tool_installer import ToolInstaller
from ai_models import SecurityScannerModel

class AISecurityScanner:
    def __init__(self, ai_model, tool_installer):
        self.ai_model = ai_model
        self.tool_installer = tool_installer
        self.running_scans = {}
        
    async def scan_target(self, target, scan_type):
        """Perform security scan with dynamic tool installation."""
        scan_config = await self.ai_model.get_scan_config(target, scan_type)
        
        installed_tools = []
        for tool_name in scan_config.get("required_tools", []):
            tool_path = self.tool_installer.install_tool_dynamically(
                scan_config.get("target_os"),
                tool_name
            )
            installed_tools.append((tool_name, tool_path))
            
        scan_id = str(uuid.uuid4())
        self.running_scans[scan_id] = {
            "status": "running",
            "tools": installed_tools,
            "results": []
        }
        
        try:
            tasks = [
                self._run_tool_scan(tool_name, tool_path, target)
                for tool_name, tool_path in installed_tools
            ]
            results = await asyncio.gather(*tasks)
            
            processed_results = await self.ai_model.process_results(results)
            self.running_scans[scan_id]["results"] = processed_results
            
            return {
                "scan_id": scan_id,
                "status": "completed",
                "results": processed_results
            }
            
        except Exception as e:
            self.running_scans[scan_id]["status"] = "error"
            self.running_scans[scan_id]["error"] = str(e)
            raise
            
    async def _run_tool_scan(self, tool_name, tool_path, target):
        """Run individual tool scan."""
        if tool_name == "nmap":
            return await self._run_nmap_scan(tool_path, target)
        elif tool_name == "nikto":
            return await self._run_nikto_scan(tool_path, target)
        elif tool_name == "sqlmap":
            return await self._run_sqlmap_scan(tool_path, target)
        
    async def _run_nmap_scan(self, tool_path, target):
        process = await asyncio.create_subprocess_exec(
            tool_path, "-sV", "-O", target,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return {
            "tool": "nmap",
            "exit_code": process.returncode,
            "stdout": stdout.decode(),
            "stderr": stderr.decode()
        }
        
    async def cancel_scan(self, scan_id):
        """Cancel running scan."""
        if scan_id in self.running_scans:
            self.running_scans[scan_id]["status"] = "cancelled"
            return True
        return False
