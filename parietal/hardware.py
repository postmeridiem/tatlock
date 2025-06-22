"""
parietal/hardware.py
Hardware and system information utilities for Tatlock.
Provides functions to query operating system, disk space, memory status, 
network statistics, and other system information.
Supports both macOS and Linux systems.
"""
import platform
import psutil
import subprocess
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
def get_operating_system_info() -> Dict[str, Any]:
    """
    Get detailed operating system information.
    Returns:
        dict: Operating system information including name, version, architecture, etc.
    """
    try:
        system_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0],
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
        }
        # Add OS-specific information
        if platform.system() == "Darwin":  # macOS
            system_info["os_type"] = "macOS"
            try:
                # Get macOS version using sw_vers
                result = subprocess.run(["sw_vers", "-productVersion"], 
                                      capture_output=True, text=True, check=True)
                system_info["macos_version"] = result.stdout.strip()
                # Get macOS build version
                result = subprocess.run(["sw_vers", "-buildVersion"], 
                                      capture_output=True, text=True, check=True)
                system_info["macos_build"] = result.stdout.strip()
                # Get macOS product name
                result = subprocess.run(["sw_vers", "-productName"], 
                                      capture_output=True, text=True, check=True)
                system_info["macos_product"] = result.stdout.strip()
            except subprocess.CalledProcessError as e:
                pass
        elif platform.system() == "Linux":
            system_info["os_type"] = "Linux"
            try:
                # Try to get Linux distribution info
                if os.path.exists("/etc/os-release"):
                    with open("/etc/os-release", "r") as f:
                        for line in f:
                            if line.startswith("PRETTY_NAME="):
                                system_info["linux_distribution"] = line.split("=", 1)[1].strip().strip('"')
                                break
                elif os.path.exists("/etc/lsb-release"):
                    with open("/etc/lsb-release", "r") as f:
                        for line in f:
                            if line.startswith("DISTRIB_DESCRIPTION="):
                                system_info["linux_distribution"] = line.split("=", 1)[1].strip().strip('"')
                                break
            except Exception as e:
                pass
        return system_info
    except Exception as e:
        return {"error": f"Failed to get OS info: {str(e)}"}
def get_disk_space_info(path: str = "/") -> Dict[str, Any]:
    """
    Get disk space information for a specific path.
    Args:
        path (str): Path to check disk space for. Defaults to "/".
    Returns:
        dict: Disk space information including total, used, free space, and usage percentage.
    """
    try:
        disk_usage = psutil.disk_usage(path)
        disk_info = {
            "path": path,
            "total_bytes": disk_usage.total,
            "used_bytes": disk_usage.used,
            "free_bytes": disk_usage.free,
            "total_gb": round(disk_usage.total / (1024**3), 2),
            "used_gb": round(disk_usage.used / (1024**3), 2),
            "free_gb": round(disk_usage.free / (1024**3), 2),
            "usage_percent": round(disk_usage.percent, 2),
            "free_percent": round(100 - disk_usage.percent, 2)
        }
        return disk_info
    except Exception as e:
        return {"error": f"Failed to get disk space info: {str(e)}"}
def get_all_disk_partitions() -> List[Dict[str, Any]]:
    """
    Get information about all disk partitions.
    Returns:
        list: List of dictionaries containing partition information.
    """
    try:
        partitions = []
        for partition in psutil.disk_partitions():
            try:
                partition_info = {
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "filesystem": partition.fstype,
                    "opts": partition.opts
                }
                # Get usage info for mounted partitions
                if partition.mountpoint and os.path.ismount(partition.mountpoint):
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        partition_info.update({
                            "total_gb": round(usage.total / (1024**3), 2),
                            "used_gb": round(usage.used / (1024**3), 2),
                            "free_gb": round(usage.free / (1024**3), 2),
                            "usage_percent": round(usage.percent, 2)
                        })
                    except Exception as e:
                        pass
                partitions.append(partition_info)
            except Exception as e:
                continue
        return partitions
    except Exception as e:
        return []
def get_memory_status() -> Dict[str, Any]:
    """
    Get detailed memory (RAM) information.
    Returns:
        dict: Memory information including total, available, used, and swap memory.
    """
    try:
        # Virtual memory (RAM)
        virtual_memory = psutil.virtual_memory()
        # Swap memory
        swap_memory = psutil.swap_memory()
        memory_info = {
            "ram": {
                "total_bytes": virtual_memory.total,
                "available_bytes": virtual_memory.available,
                "used_bytes": virtual_memory.used,
                "free_bytes": virtual_memory.free,
                "total_gb": round(virtual_memory.total / (1024**3), 2),
                "available_gb": round(virtual_memory.available / (1024**3), 2),
                "used_gb": round(virtual_memory.used / (1024**3), 2),
                "free_gb": round(virtual_memory.free / (1024**3), 2),
                "usage_percent": round(virtual_memory.percent, 2),
                "available_percent": round(100 - virtual_memory.percent, 2)
            },
            "swap": {
                "total_bytes": swap_memory.total,
                "used_bytes": swap_memory.used,
                "free_bytes": swap_memory.free,
                "total_gb": round(swap_memory.total / (1024**3), 2),
                "used_gb": round(swap_memory.used / (1024**3), 2),
                "free_gb": round(swap_memory.free / (1024**3), 2),
                "usage_percent": round(swap_memory.percent, 2)
            }
        }
        return memory_info
    except Exception as e:
        return {"error": f"Failed to get memory status: {str(e)}"}
def get_cpu_info() -> Dict[str, Any]:
    """
    Get CPU information and usage statistics.
    Returns:
        dict: CPU information including cores, frequency, and usage statistics.
    """
    try:
        # CPU count
        cpu_count = {
            "physical": psutil.cpu_count(logical=False),
            "logical": psutil.cpu_count(logical=True)
        }
        # CPU frequency
        cpu_freq = psutil.cpu_freq()
        freq_info = {}
        if cpu_freq:
            freq_info = {
                "current_mhz": round(cpu_freq.current, 2),
                "min_mhz": round(cpu_freq.min, 2) if cpu_freq.min else None,
                "max_mhz": round(cpu_freq.max, 2) if cpu_freq.max else None,
                "current_ghz": round(cpu_freq.current / 1000, 2),
                "min_ghz": round(cpu_freq.min / 1000, 2) if cpu_freq.min else None,
                "max_ghz": round(cpu_freq.max / 1000, 2) if cpu_freq.max else None
            }
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_percent_per_core = psutil.cpu_percent(interval=1, percpu=True)
        cpu_info = {
            "count": cpu_count,
            "frequency": freq_info,
            "usage": {
                "overall_percent": round(cpu_percent, 2),
                "per_core_percent": [round(p, 2) for p in cpu_percent_per_core]
            },
            "load_average": get_load_average()
        }
        return cpu_info
    except Exception as e:
        return {"error": f"Failed to get CPU info: {str(e)}"}
def get_load_average() -> Dict[str, float]:
    """
    Get system load average (Linux) or similar metrics (macOS).
    Returns:
        dict: Load average information.
    """
    try:
        if platform.system() == "Linux":
            # Linux load average
            load_avg = os.getloadavg()
            return {
                "1min": round(load_avg[0], 2),
                "5min": round(load_avg[1], 2),
                "15min": round(load_avg[2], 2)
            }
        elif platform.system() == "Darwin":
            # macOS - use psutil for load average
            try:
                # Try to get load average using sysctl
                result = subprocess.run(["sysctl", "-n", "vm.loadavg"], 
                                      capture_output=True, text=True, check=True)
                load_values = result.stdout.strip().split()
                return {
                    "1min": round(float(load_values[0]), 2),
                    "5min": round(float(load_values[1]), 2),
                    "15min": round(float(load_values[2]), 2)
                }
            except (subprocess.CalledProcessError, (ValueError, IndexError)):
                # Fallback to psutil
                load_avg = psutil.getloadavg()
                return {
                    "1min": round(load_avg[0], 2),
                    "5min": round(load_avg[1], 2),
                    "15min": round(load_avg[2], 2)
                }
        else:
            return {"error": "Load average not available on this system"}
    except Exception as e:
        return {"error": f"Failed to get load average: {str(e)}"}
def get_network_statistics() -> Dict[str, Any]:
    """
    Get network interface statistics.
    Returns:
        dict: Network statistics including bytes sent/received and interface information.
    """
    try:
        # Network I/O counters
        net_io = psutil.net_io_counters()
        # Network interfaces
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()
        interfaces = []
        for interface_name, addresses in net_if_addrs.items():
            interface_info = {
                "name": interface_name,
                "addresses": []
            }
            # Get interface statistics
            if interface_name in net_if_stats:
                stats = net_if_stats[interface_name]
                interface_info.update({
                    "is_up": stats.isup,
                    "speed_mbps": stats.speed if stats.speed > 0 else None,
                    "mtu": stats.mtu
                })
            # Get addresses for this interface
            for addr in addresses:
                addr_info = {
                    "family": str(addr.family),
                    "address": addr.address,
                    "netmask": addr.netmask,
                    "broadcast": addr.broadcast if hasattr(addr, 'broadcast') else None
                }
                interface_info["addresses"].append(addr_info)
            interfaces.append(interface_info)
        network_info = {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "bytes_sent_gb": round(net_io.bytes_sent / (1024**3), 2),
            "bytes_recv_gb": round(net_io.bytes_recv / (1024**3), 2),
            "interfaces": interfaces
        }
        return network_info
    except Exception as e:
        return {"error": f"Failed to get network statistics: {str(e)}"}
def get_system_uptime() -> Dict[str, Any]:
    """
    Get system uptime information.
    Returns:
        dict: Uptime information including boot time and uptime duration.
    """
    try:
        boot_time = psutil.boot_time()
        uptime_seconds = datetime.now().timestamp() - boot_time
        # Convert to days, hours, minutes
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)
        uptime_info = {
            "boot_time": datetime.fromtimestamp(boot_time).isoformat(),
            "uptime_seconds": int(uptime_seconds),
            "uptime_formatted": f"{days}d {hours}h {minutes}m {seconds}s",
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds
        }
        return uptime_info
    except Exception as e:
        return {"error": f"Failed to get system uptime: {str(e)}"}
def get_process_count() -> Dict[str, int]:
    """
    Get count of running processes.
    Returns:
        dict: Process count information.
    """
    try:
        processes = list(psutil.process_iter(['pid', 'name', 'status']))
        process_info = {
            "total": len(processes),
            "running": len([p for p in processes if p.info['status'] == 'running']),
            "sleeping": len([p for p in processes if p.info['status'] == 'sleeping']),
            "stopped": len([p for p in processes if p.info['status'] == 'stopped']),
            "zombie": len([p for p in processes if p.info['status'] == 'zombie'])
        }
        return process_info
    except Exception as e:
        return {"error": f"Failed to get process count: {str(e)}"}
def get_comprehensive_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information including all hardware and system metrics.
    Returns:
        dict: Complete system information.
    """
    try:
        system_info = {
            "timestamp": datetime.now().isoformat(),
            "operating_system": get_operating_system_info(),
            "cpu": get_cpu_info(),
            "memory": get_memory_status(),
            "disk": {
                "root_partition": get_disk_space_info("/"),
                "all_partitions": get_all_disk_partitions()
            },
            "network": get_network_statistics(),
            "uptime": get_system_uptime(),
            "processes": get_process_count()
        }
        return system_info
    except Exception as e:
        return {"error": f"Failed to get comprehensive system info: {str(e)}"}
def check_system_health() -> Dict[str, Any]:
    """
    Perform a system health check and return status indicators.
    Returns:
        dict: System health status with warnings and recommendations.
    """
    try:
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "warnings": [],
            "recommendations": []
        }
        # Check memory usage
        memory = get_memory_status()
        if memory.get("ram", {}).get("usage_percent", 0) > 90:
            health_status["warnings"].append("High memory usage (>90%)")
            health_status["overall_status"] = "warning"
        elif memory.get("ram", {}).get("usage_percent", 0) > 80:
            health_status["recommendations"].append("Consider monitoring memory usage (>80%)")
        # Check disk usage
        disk = get_disk_space_info("/")
        if disk.get("usage_percent", 0) > 95:
            health_status["warnings"].append("Critical disk usage (>95%)")
            health_status["overall_status"] = "critical"
        elif disk.get("usage_percent", 0) > 90:
            health_status["warnings"].append("High disk usage (>90%)")
            health_status["overall_status"] = "warning"
        elif disk.get("usage_percent", 0) > 80:
            health_status["recommendations"].append("Consider monitoring disk usage (>80%)")
        # Check CPU usage
        cpu = get_cpu_info()
        if cpu.get("usage", {}).get("overall_percent", 0) > 90:
            health_status["warnings"].append("High CPU usage (>90%)")
            health_status["overall_status"] = "warning"
        # Check load average (Linux)
        if platform.system() == "Linux":
            load_avg = cpu.get("load_average", {})
            cpu_count = cpu.get("count", {}).get("logical", 1)
            if load_avg.get("5min", 0) > cpu_count * 2:
                health_status["warnings"].append("High system load")
                health_status["overall_status"] = "warning"
        return health_status
    except Exception as e:
        return {"error": f"Failed to perform system health check: {str(e)}"} 