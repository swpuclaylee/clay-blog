from pydantic import BaseModel


class DashboardStats(BaseModel):
    articleCount: int
    commentCount: int
    userCount: int
    totalViews: int
