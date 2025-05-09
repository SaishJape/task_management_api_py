import time
from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse

from core.config import settings
from models.user import UserInDB
from models.task import TaskInDB

class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.client = None
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        retry_count = 0
        max_retries = 5
        
        while retry_count < max_retries:
            try:
                self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
                # Create collections if they don't exist
                self._create_collections()
                break
            except Exception as e:
                retry_count += 1
                wait_time = 2 ** retry_count  # Exponential backoff
                print(f"Failed to connect to Qdrant. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                
        if retry_count == max_retries:
            raise Exception("Failed to connect to Qdrant after multiple attempts")
    
    def _create_collections(self):
        # Create users collection
        try:
            self.client.get_collection("users")
        except (UnexpectedResponse, Exception):
            self.client.create_collection(
                collection_name="users",
                vectors_config=models.VectorParams(size=1, distance=models.Distance.COSINE),
            )
        
        # Create tasks collection
        try:
            self.client.get_collection("tasks")
        except (UnexpectedResponse, Exception):
            self.client.create_collection(
                collection_name="tasks",
                vectors_config=models.VectorParams(size=1, distance=models.Distance.COSINE),
            )
    
    def create_user(self, user: UserInDB) -> str:
        user_dict = user.model_dump()
        # Use a placeholder vector since we're mainly using Qdrant as a document store
        self.client.upsert(
            collection_name="users",
            points=[
                models.PointStruct(
                    id=user.id,
                    vector=[0.0],  # Placeholder vector
                    payload=user_dict
                )
            ]
        )
        return user.id
    
    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        results = self.client.scroll(
            collection_name="users",
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="email",
                        match=models.MatchValue(value=email)
                    )
                ]
            ),
            limit=1
        )
        
        if results[0]:  # Check if we got any results
            user_data = results[0][0].payload
            return UserInDB(**user_data)
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        try:
            result = self.client.retrieve(
                collection_name="users",
                ids=[user_id]
            )
            if result:
                return UserInDB(**result[0].payload)
        except Exception:
            pass
        return None
    
    def get_all_users(self) -> List[UserInDB]:
        """Get all users from the database"""
        results = self.client.scroll(
            collection_name="users",
            limit=100  # In a real app, you'd implement pagination
        )
        
        if results[0]:  # Check if we got any results
            return [UserInDB(**point.payload) for point in results[0]]
        return []
    
    def create_task(self, task: TaskInDB) -> str:
        task_dict = task.model_dump()
        self.client.upsert(
            collection_name="tasks",
            points=[
                models.PointStruct(
                    id=task.id,
                    vector=[0.0],  # Placeholder vector
                    payload=task_dict
                )
            ]
        )
        return task.id
    
    def get_task_by_id(self, task_id: str) -> Optional[TaskInDB]:
        try:
            result = self.client.retrieve(
                collection_name="tasks",
                ids=[task_id]
            )
            if result:
                return TaskInDB(**result[0].payload)
        except Exception:
            pass
        return None
    
    def get_tasks_by_user(self, user_id: str) -> List[TaskInDB]:
        results = self.client.scroll(
            collection_name="tasks",
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="assigned_to",
                        match=models.MatchValue(value=user_id)
                    )
                ]
            ),
            limit=100
        )
        
        if results[0]:  # Check if we got any results
            return [TaskInDB(**point.payload) for point in results[0]]
        return []
    
    def assign_task(self, task_id: str, user_id: str) -> bool:
        task = self.get_task_by_id(task_id)
        if not task:
            return False
        
        task.assigned_to = user_id
        task_dict = task.model_dump()
        
        self.client.upsert(
            collection_name="tasks",
            points=[
                models.PointStruct(
                    id=task.id,
                    vector=[0.0],  # Placeholder vector
                    payload=task_dict
                )
            ]
        )
        return True

db_manager = DatabaseManager()