from pydantic import BaseModel, Field

from src.models.file import FileCategory
from src.schemas.mixins import IDMixin, ORMConfigMixin, TimestampMixin

# ========== Base ==========


class FileBase(BaseModel):
    """文件基础字段"""

    name: str
    category: FileCategory
    file_extension: str
    file_size: int
    minio_object_name: str


# ========== Response ==========


class FileResponse(IDMixin, FileBase, TimestampMixin, ORMConfigMixin):
    """文件详情响应"""

    download_url: str | None = None


class FileListItem(IDMixin, ORMConfigMixin, TimestampMixin):
    """文件列表项响应（精简）"""

    name: str
    category: FileCategory
    file_extension: str
    file_size: int
    download_url: str | None = None


class FileUploadError(BaseModel):
    """文件上传错误信息"""

    filename: str
    error: str


class BatchUploadResponse(BaseModel):
    """批量上传响应"""

    success_count: int = Field(0, description="成功上传数量")
    failed_count: int = Field(0, description="失败上传数量")
    total_count: int = Field(0, description="总文件数")
    files: list[FileResponse] = Field(default_factory=list, description="成功上传的文件列表")
    errors: list[FileUploadError] = Field(default_factory=list, description="失败的文件列表")


# ========== 分片上传 Request ==========


class MultipartInitRequest(BaseModel):
    """初始化分片上传请求"""

    filename: str = Field(..., description="文件名")
    category: FileCategory = Field(..., description="文件分类")
    file_size: int = Field(..., gt=0, description="文件大小（字节）")
    chunk_size: int = Field(..., gt=0, description="分片大小（字节）")


class MultipartCompleteRequest(BaseModel):
    """完成分片上传请求"""

    object_name: str = Field(..., description="MinIO对象名称")
    parts: list[dict] = Field(
        ..., description="分片列表 [{'part_number': 1, 'etag': 'xxx'}]"
    )
    filename: str = Field(..., description="文件名")
    category: FileCategory = Field(..., description="文件分类")
    file_size: int = Field(..., gt=0, description="文件大小（字节）")


class MultipartAbortRequest(BaseModel):
    """取消分片上传请求"""

    object_name: str = Field(..., description="MinIO对象名称")


# ========== 分片上传 Response ==========


class MultipartInitResponse(BaseModel):
    """初始化分片上传响应"""

    upload_id: str = Field(..., description="上传会话ID")
    object_name: str = Field(..., description="MinIO对象名称")
    total_chunks: int = Field(..., description="总分片数")
    chunk_size: int = Field(..., description="分片大小（字节）")


class MultipartChunkResponse(BaseModel):
    """上传分片响应"""

    upload_id: str = Field(..., description="上传会话ID")
    part_number: int = Field(..., description="分片编号")
    etag: str = Field(..., description="分片标识")
