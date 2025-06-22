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
    Perform a basic system health check.
    Returns:
        dict: System health status and recommendations.
    """
    try:
        health_status = {
            "overall_status": "healthy",
            "checks": {},
            "recommendations": []
        }
        
        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            health_status["checks"]["cpu"] = {"status": "warning", "message": f"High CPU usage: {cpu_percent}%"}
            health_status["recommendations"].append("Consider closing unnecessary applications")
        else:
            health_status["checks"]["cpu"] = {"status": "good", "message": f"CPU usage: {cpu_percent}%"}
        
        # Check memory usage
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            health_status["checks"]["memory"] = {"status": "warning", "message": f"High memory usage: {memory.percent}%"}
            health_status["recommendations"].append("Consider freeing up memory or adding more RAM")
        else:
            health_status["checks"]["memory"] = {"status": "good", "message": f"Memory usage: {memory.percent}%"}
        
        # Check disk usage
        disk = psutil.disk_usage('/')
        if disk.percent > 90:
            health_status["checks"]["disk"] = {"status": "warning", "message": f"High disk usage: {disk.percent}%"}
            health_status["recommendations"].append("Consider freeing up disk space")
        else:
            health_status["checks"]["disk"] = {"status": "good", "message": f"Disk usage: {disk.percent}%"}
        
        # Check if any warnings were found
        warnings = [check for check in health_status["checks"].values() if check["status"] == "warning"]
        if warnings:
            health_status["overall_status"] = "warning"
        
        return health_status
    except Exception as e:
        return {"error": f"Failed to check system health: {str(e)}"}
def run_llm_benchmark() -> Dict[str, Any]:
    """
    Run a benchmark test for LLM performance.
    Returns:
        dict: Benchmark results including response times and analysis.
    """
    import time
    import ollama
    from config import OLLAMA_MODEL
    
    benchmark_results = {
        "timestamp": datetime.now().isoformat(),
        "model": OLLAMA_MODEL,
        "tests": {},
        "summary": {},
        "analysis": {}
    }
    
    try:
        # Test 1: Simple response time
        start_time = time.time()
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": "Say 'Hello' and nothing else."}]
        )
        simple_time = time.time() - start_time
        
        benchmark_results["tests"]["simple_response"] = {
            "time_seconds": round(simple_time, 3),
            "status": "success",
            "response_length": len(response['message']['content'])
        }
        
        # Test 2: Complex reasoning
        start_time = time.time()
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": "Explain quantum computing in 2 sentences."}]
        )
        complex_time = time.time() - start_time
        
        benchmark_results["tests"]["complex_reasoning"] = {
            "time_seconds": round(complex_time, 3),
            "status": "success",
            "response_length": len(response['message']['content'])
        }
        
        # Test 3: Tool calling (if available)
        try:
            start_time = time.time()
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": "What's the weather like today?"}],
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "get_weather_forecast",
                        "description": "Get weather forecast for a city",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string", "description": "City name"}
                            },
                            "required": ["city"]
                        }
                    }
                }]
            )
            tool_time = time.time() - start_time
            
            benchmark_results["tests"]["tool_calling"] = {
                "time_seconds": round(tool_time, 3),
                "status": "success",
                "has_tool_calls": bool(response['message'].get('tool_calls')),
                "response_length": len(response['message']['content'])
            }
        except Exception as e:
            benchmark_results["tests"]["tool_calling"] = {
                "time_seconds": 0,
                "status": "failed",
                "error": str(e)
            }
        
        # Calculate summary statistics
        successful_tests = [test for test in benchmark_results["tests"].values() if test["status"] == "success"]
        if successful_tests:
            times = [test["time_seconds"] for test in successful_tests]
            benchmark_results["summary"] = {
                "total_tests": len(benchmark_results["tests"]),
                "successful_tests": len(successful_tests),
                "average_time": round(sum(times) / len(times), 3),
                "min_time": round(min(times), 3),
                "max_time": round(max(times), 3),
                "total_time": round(sum(times), 3)
            }
            
            # Performance analysis
            avg_time = benchmark_results["summary"]["average_time"]
            if avg_time < 2.0:
                performance_grade = "Excellent"
                performance_note = "Very fast response times"
            elif avg_time < 5.0:
                performance_grade = "Good"
                performance_note = "Acceptable response times"
            elif avg_time < 10.0:
                performance_grade = "Fair"
                performance_note = "Response times could be improved"
            else:
                performance_grade = "Poor"
                performance_note = "Response times are too slow"
            
            benchmark_results["analysis"] = {
                "performance_grade": performance_grade,
                "performance_note": performance_note,
                "recommendations": []
            }
            
            if avg_time > 5.0:
                benchmark_results["analysis"]["recommendations"].append("Consider using a faster model or optimizing system resources")
            if benchmark_results["tests"].get("tool_calling", {}).get("status") == "failed":
                benchmark_results["analysis"]["recommendations"].append("Tool calling functionality may need configuration")
        
        return benchmark_results
        
    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "model": OLLAMA_MODEL,
            "error": f"Benchmark failed: {str(e)}",
            "tests": {},
            "summary": {},
            "analysis": {}
        }
def run_tool_benchmark() -> Dict[str, Any]:
    """
    Run a benchmark test for tool performance.
    Returns:
        dict: Benchmark results for various tools.
    """
    import time
    from stem.tools import (
        execute_find_personal_variables,
        execute_get_weather_forecast,
        execute_web_search,
        execute_recall_memories
    )
    
    benchmark_results = {
        "timestamp": datetime.now().isoformat(),
        "tools": {},
        "summary": {},
        "analysis": {}
    }
    
    try:
        # Test personal variables tool
        start_time = time.time()
        try:
            result = execute_find_personal_variables(searchkey="name")
            tool_time = time.time() - start_time
            benchmark_results["tools"]["personal_variables"] = {
                "time_seconds": round(tool_time, 3),
                "status": "success",
                "result_size": len(str(result))
            }
        except Exception as e:
            benchmark_results["tools"]["personal_variables"] = {
                "time_seconds": 0,
                "status": "failed",
                "error": str(e)
            }
        
        # Test memory recall tool
        start_time = time.time()
        try:
            result = execute_recall_memories(keyword="test", username="admin")
            tool_time = time.time() - start_time
            benchmark_results["tools"]["memory_recall"] = {
                "time_seconds": round(tool_time, 3),
                "status": "success",
                "result_size": len(str(result))
            }
        except Exception as e:
            benchmark_results["tools"]["memory_recall"] = {
                "time_seconds": 0,
                "status": "failed",
                "error": str(e)
            }
        
        # Test weather tool (if API key available)
        start_time = time.time()
        try:
            result = execute_get_weather_forecast(city="Rotterdam")
            tool_time = time.time() - start_time
            benchmark_results["tools"]["weather_forecast"] = {
                "time_seconds": round(tool_time, 3),
                "status": "success",
                "result_size": len(str(result))
            }
        except Exception as e:
            benchmark_results["tools"]["weather_forecast"] = {
                "time_seconds": 0,
                "status": "failed",
                "error": str(e)
            }
        
        # Test web search tool (if API key available)
        start_time = time.time()
        try:
            result = execute_web_search(query="test")
            tool_time = time.time() - start_time
            benchmark_results["tools"]["web_search"] = {
                "time_seconds": round(tool_time, 3),
                "status": "success",
                "result_size": len(str(result))
            }
        except Exception as e:
            benchmark_results["tools"]["web_search"] = {
                "time_seconds": 0,
                "status": "failed",
                "error": str(e)
            }
        
        # Calculate summary statistics
        successful_tools = [tool for tool in benchmark_results["tools"].values() if tool["status"] == "success"]
        if successful_tools:
            times = [tool["time_seconds"] for tool in successful_tools]
            benchmark_results["summary"] = {
                "total_tools": len(benchmark_results["tools"]),
                "successful_tools": len(successful_tools),
                "average_time": round(sum(times) / len(times), 3),
                "min_time": round(min(times), 3),
                "max_time": round(max(times), 3),
                "total_time": round(sum(times), 3)
            }
            
            # Performance analysis
            avg_time = benchmark_results["summary"]["average_time"]
            if avg_time < 0.5:
                performance_grade = "Excellent"
                performance_note = "Very fast tool execution"
            elif avg_time < 2.0:
                performance_grade = "Good"
                performance_note = "Acceptable tool execution times"
            elif avg_time < 5.0:
                performance_grade = "Fair"
                performance_note = "Tool execution could be faster"
            else:
                performance_grade = "Poor"
                performance_note = "Tool execution is too slow"
            
            benchmark_results["analysis"] = {
                "performance_grade": performance_grade,
                "performance_note": performance_note,
                "recommendations": []
            }
            
            # Check for failed tools
            failed_tools = [name for name, tool in benchmark_results["tools"].items() if tool["status"] == "failed"]
            if failed_tools:
                benchmark_results["analysis"]["recommendations"].append(f"Fix configuration for failed tools: {', '.join(failed_tools)}")
            
            if avg_time > 2.0:
                benchmark_results["analysis"]["recommendations"].append("Consider optimizing tool execution or checking network connectivity")
        
        return benchmark_results
        
    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "error": f"Tool benchmark failed: {str(e)}",
            "tools": {},
            "summary": {},
            "analysis": {}
        }
def run_comprehensive_benchmark() -> Dict[str, Any]:
    """
    Run a comprehensive benchmark including LLM and tools.
    Returns:
        dict: Complete benchmark results with system analysis.
    """
    comprehensive_results = {
        "timestamp": datetime.now().isoformat(),
        "system_info": get_comprehensive_system_info(),
        "llm_benchmark": run_llm_benchmark(),
        "tool_benchmark": run_tool_benchmark(),
        "overall_analysis": {}
    }
    
    try:
        # Overall performance analysis
        llm_summary = comprehensive_results["llm_benchmark"].get("summary", {})
        tool_summary = comprehensive_results["tool_benchmark"].get("summary", {})
        
        overall_analysis = {
            "total_benchmark_time": 0,
            "performance_grade": "Unknown",
            "bottlenecks": [],
            "recommendations": []
        }
        
        if llm_summary and tool_summary:
            total_time = llm_summary.get("total_time", 0) + tool_summary.get("total_time", 0)
            overall_analysis["total_benchmark_time"] = round(total_time, 3)
            
            llm_avg = llm_summary.get("average_time", 0)
            tool_avg = tool_summary.get("average_time", 0)
            
            # Determine overall grade
            if llm_avg < 3.0 and tool_avg < 1.0:
                overall_analysis["performance_grade"] = "Excellent"
            elif llm_avg < 6.0 and tool_avg < 2.0:
                overall_analysis["performance_grade"] = "Good"
            elif llm_avg < 12.0 and tool_avg < 5.0:
                overall_analysis["performance_grade"] = "Fair"
            else:
                overall_analysis["performance_grade"] = "Poor"
            
            # Identify bottlenecks
            if llm_avg > 5.0:
                overall_analysis["bottlenecks"].append("LLM response time is slow")
            if tool_avg > 2.0:
                overall_analysis["bottlenecks"].append("Tool execution is slow")
            
            # System resource analysis
            system_info = comprehensive_results["system_info"]
            cpu_usage = system_info.get("cpu", {}).get("usage", {}).get("overall_percent", 0)
            memory_usage = system_info.get("memory", {}).get("ram", {}).get("usage_percent", 0)
            
            if cpu_usage > 80:
                overall_analysis["bottlenecks"].append("High CPU usage may be affecting performance")
            if memory_usage > 80:
                overall_analysis["bottlenecks"].append("High memory usage may be affecting performance")
            
            # Generate recommendations
            if overall_analysis["performance_grade"] in ["Fair", "Poor"]:
                overall_analysis["recommendations"].append("Consider upgrading system resources or optimizing configuration")
            if llm_avg > 5.0:
                overall_analysis["recommendations"].append("Consider using a faster LLM model or optimizing model parameters")
            if tool_avg > 2.0:
                overall_analysis["recommendations"].append("Check network connectivity and API key configurations")
        
        comprehensive_results["overall_analysis"] = overall_analysis
        return comprehensive_results
        
    except Exception as e:
        comprehensive_results["error"] = f"Comprehensive benchmark failed: {str(e)}"
        return comprehensive_results 