# utils/progress_tracker.py
"""
Progress tracking utility for long-running operations
"""

import threading
import time
import logging
from typing import Dict, Any, Optional, Callable

class ProgressTracker:
    """
    Tracks progress of long-running operations
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.operations: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
        
        self.logger.info("ProgressTracker initialized")
    
    def start_operation(self, operation_id: str, total_steps: int = 100, 
                       description: str = "") -> None:
        """
        Start tracking a new operation
        
        Args:
            operation_id: Unique identifier for the operation
            total_steps: Total number of steps in the operation
            description: Description of the operation
        """
        with self.lock:
            self.operations[operation_id] = {
                'current_step': 0,
                'total_steps': total_steps,
                'description': description,
                'start_time': time.time(),
                'callback': None,
                'completed': False,
                'error': None
            }
        
        self.logger.info(f"Started tracking operation: {operation_id}")
    
    def update_progress(self, operation_id: str, current_step: int, 
                       message: str = "") -> None:
        """
        Update progress of an operation
        
        Args:
            operation_id: Operation identifier
            current_step: Current step number
            message: Optional progress message
        """
        with self.lock:
            if operation_id not in self.operations:
                self.logger.warning(f"Unknown operation: {operation_id}")
                return
            
            operation = self.operations[operation_id]
            operation['current_step'] = current_step
            operation['message'] = message
            
            # Calculate progress percentage
            progress = (current_step / operation['total_steps']) * 100
            
            # Call callback if registered
            if operation['callback']:
                try:
                    operation['callback'](progress, message)
                except Exception as e:
                    self.logger.error(f"Error in progress callback: {e}")
        
        self.logger.debug(f"Updated progress for {operation_id}: {current_step}/{operation['total_steps']}")
    
    def set_callback(self, operation_id: str, callback: Callable[[float, str], None]) -> None:
        """
        Set progress callback for an operation
        
        Args:
            operation_id: Operation identifier
            callback: Callback function (progress, message) -> None
        """
        with self.lock:
            if operation_id in self.operations:
                self.operations[operation_id]['callback'] = callback
    
    def get_progress(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current progress information
        
        Args:
            operation_id: Operation identifier
            
        Returns:
            Progress information dictionary or None if not found
        """
        with self.lock:
            if operation_id not in self.operations:
                return None
            
            operation = self.operations[operation_id]
            
            # Calculate progress percentage
            progress = (operation['current_step'] / operation['total_steps']) * 100
            
            # Calculate elapsed time
            elapsed = time.time() - operation['start_time']
            
            # Estimate remaining time
            if progress > 0:
                estimated_total = elapsed / (progress / 100)
                remaining = estimated_total - elapsed
            else:
                remaining = None
            
            return {
                'operation_id': operation_id,
                'current_step': operation['current_step'],
                'total_steps': operation['total_steps'],
                'progress': progress,
                'description': operation['description'],
                'message': operation.get('message', ''),
                'elapsed_time': elapsed,
                'estimated_remaining': remaining,
                'completed': operation['completed'],
                'error': operation['error']
            }
    
    def complete_operation(self, operation_id: str, success: bool = True, 
                          error: str = None) -> None:
        """
        Mark an operation as completed
        
        Args:
            operation_id: Operation identifier
            success: Whether operation completed successfully
            error: Error message if operation failed
        """
        with self.lock:
            if operation_id not in self.operations:
                self.logger.warning(f"Unknown operation: {operation_id}")
                return
            
            operation = self.operations[operation_id]
            operation['completed'] = True
            operation['success'] = success
            operation['error'] = error
            
            # Calculate final progress
            if success:
                operation['current_step'] = operation['total_steps']
                progress = 100.0
            else:
                progress = (operation['current_step'] / operation['total_steps']) * 100
            
            # Call callback if registered
            if operation['callback']:
                try:
                    operation['callback'](progress, "Completed" if success else f"Error: {error}")
                except Exception as e:
                    self.logger.error(f"Error in progress callback: {e}")
        
        status = "completed successfully" if success else f"failed: {error}"
        self.logger.info(f"Operation {operation_id} {status}")
    
    def cancel_operation(self, operation_id: str) -> None:
        """
        Cancel an operation
        
        Args:
            operation_id: Operation identifier
        """
        with self.lock:
            if operation_id in self.operations:
                self.operations[operation_id]['cancelled'] = True
                self.logger.info(f"Operation {operation_id} cancelled")
    
    def is_operation_active(self, operation_id: str) -> bool:
        """
        Check if an operation is still active
        
        Args:
            operation_id: Operation identifier
            
        Returns:
            True if operation is active, False otherwise
        """
        with self.lock:
            if operation_id not in self.operations:
                return False
            
            operation = self.operations[operation_id]
            return not operation['completed'] and not operation.get('cancelled', False)
    
    def get_active_operations(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active operations
        
        Returns:
            Dictionary of active operations
        """
        with self.lock:
            return {
                op_id: op_data for op_id, op_data in self.operations.items()
                if not op_data['completed'] and not op_data.get('cancelled', False)
            }
    
    def cleanup_operation(self, operation_id: str) -> None:
        """
        Remove completed operation from tracking
        
        Args:
            operation_id: Operation identifier
        """
        with self.lock:
            if operation_id in self.operations:
                del self.operations[operation_id]
                self.logger.debug(f"Cleaned up operation: {operation_id}")
    
    def cleanup_all_operations(self) -> None:
        """Remove all completed operations"""
        with self.lock:
            completed_ops = [
                op_id for op_id, op_data in self.operations.items()
                if op_data['completed'] or op_data.get('cancelled', False)
            ]
            
            for op_id in completed_ops:
                del self.operations[op_id]
            
            self.logger.debug(f"Cleaned up {len(completed_ops)} completed operations")

# Test the progress_tracker
if __name__ == "__main__":
    import logging
    
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Create progress tracker
    tracker = ProgressTracker()
    
    # Test callback function
    def progress_callback(progress: float, message: str):
        print(f"Progress: {progress:.1f}% - {message}")
    
    # Start an operation
    tracker.start_operation("test_op", 100, "Test Operation")
    tracker.set_callback("test_op", progress_callback)
    
    # Simulate progress updates
    import time
    
    def simulate_operation():
        for i in range(101):
            tracker.update_progress("test_op", i, f"Processing step {i}")
            time.sleep(0.05)
        
        tracker.complete_operation("test_op", True)
    
    # Run simulation in separate thread
    thread = threading.Thread(target=simulate_operation)
    thread.daemon = True
    thread.start()
    
    # Monitor progress
    while tracker.is_operation_active("test_op"):
        progress_info = tracker.get_progress("test_op")
        if progress_info:
            print(f"Active operation: {progress_info['operation_id']} - {progress_info['progress']:.1f}%")
        time.sleep(1)
    
    print("Test completed")