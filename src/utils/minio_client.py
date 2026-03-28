import io
import os
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import UploadFile
from loguru import logger
from minio import Minio
from minio.datatypes import Part
from minio.error import S3Error

from src.core.config import settings


class MinioClient:
    """
    MinIO 对象存储客户端

    功能：
    - 存储桶管理
    - 文件上传（UploadFile、本地文件、字节流）
    - 预签名 URL 生成
    - 文件删除和检查
    """

    def __init__(
        self,
        endpoint: str = None,
        access_key: str = None,
        secret_key: str = None,
        secure: bool = None,
    ):
        """
        初始化 MinIO 客户端

        Args:
            endpoint: MinIO 服务器地址，默认从配置读取
            access_key: 访问密钥，默认从配置读取
            secret_key: 秘密密钥，默认从配置读取
            secure: 是否使用 HTTPS，默认从配置读取
        """
        self.endpoint = endpoint or settings.MINIO_ENDPOINT
        self.access_key = access_key or settings.MINIO_ACCESS_KEY
        self.secret_key = secret_key or settings.MINIO_SECRET_KEY
        self.secure = secure if secure is not None else settings.MINIO_SECURE

        # 创建 MinIO 客户端
        self.client = Minio(
            endpoint=self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )

        logger.info(f"MinIO 客户端初始化成功: {self.endpoint}")

    # ==================== 存储桶管理 ====================

    def ensure_bucket(self, bucket_name: str) -> bool:
        """
        确保存储桶存在，不存在则创建

        Args:
            bucket_name: 存储桶名称

        Returns:
            是否成功
        """
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                logger.info(f"存储桶创建成功: {bucket_name}")
            return True
        except S3Error as e:
            logger.error(f"存储桶操作失败: {e}")
            return False

    def bucket_exists(self, bucket_name: str) -> bool:
        """
        检查存储桶是否存在

        Args:
            bucket_name: 存储桶名称

        Returns:
            是否存在
        """
        try:
            return self.client.bucket_exists(bucket_name)
        except S3Error as e:
            logger.error(f"检查存储桶失败: {e}")
            return False

    # ==================== 文件上传 ====================

    def _generate_object_name(self, filename: str, folder: str = None) -> str:
        """
        生成对象名称（文件名 + 时间戳）

        Args:
            filename: 原始文件名
            folder: 文件夹路径（可选）

        Returns:
            对象名称
        """
        # 提取文件名和扩展名
        name = Path(filename).stem
        ext = Path(filename).suffix

        # 添加时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        object_name = f"{name}_{timestamp}{ext}"

        # 添加文件夹前缀
        if folder:
            folder = folder.strip("/")
            object_name = f"{folder}/{object_name}"

        return object_name

    async def upload_file(
        self,
        file: UploadFile,
        bucket_name: str = None,
        folder: str = None,
        object_name: str = None,
    ) -> dict:
        """
        上传 FastAPI UploadFile 到 MinIO

        Args:
            file: FastAPI 上传的文件对象
            bucket_name: 存储桶名称，默认使用配置中的桶
            folder: 文件夹路径（可选）

        Returns:
            上传结果字典
        """
        bucket_name = bucket_name or settings.MINIO_BUCKET

        try:
            # 确保存储桶存在
            if not self.ensure_bucket(bucket_name):
                return {"success": False, "error": "存储桶创建失败"}

            # 读取文件内容
            file_content = await file.read()
            await file.seek(0)

            # 生成对象名称
            if object_name is None:
                object_name = self._generate_object_name(file.filename, folder)

            # 上传文件
            self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=io.BytesIO(file_content),
                length=len(file_content),
                content_type=file.content_type,
            )

            logger.info(f"文件上传成功: {bucket_name}/{object_name}")

            return {
                "success": True,
                "bucket_name": bucket_name,
                "object_name": object_name,
                "file_size": len(file_content),
                "content_type": file.content_type,
                "original_filename": file.filename,
            }

        except Exception as e:
            logger.error(f"上传文件失败: {e}")
            return {"success": False, "error": str(e)}

    def upload_file_from_path(
        self,
        file_path: str,
        bucket_name: str = None,
        folder: str = None,
        object_name: str = None,
    ) -> dict:
        """
        上传本地文件到 MinIO

        Args:
            file_path: 本地文件路径
            bucket_name: 存储桶名称
            folder: 文件夹路径（可选）
            object_name: 自定义对象名称（可选，默认使用文件名+时间戳）

        Returns:
            上传结果字典
        """
        bucket_name = bucket_name or settings.MINIO_BUCKET

        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return {"success": False, "error": f"文件不存在: {file_path}"}

            # 确保存储桶存在
            if not self.ensure_bucket(bucket_name):
                return {"success": False, "error": "存储桶创建失败"}

            # 生成对象名称
            if object_name is None:
                filename = os.path.basename(file_path)
                object_name = self._generate_object_name(filename, folder)
            elif folder:
                folder = folder.strip("/")
                object_name = f"{folder}/{object_name}"

            # 获取文件信息
            file_size = os.path.getsize(file_path)

            # 检测 MIME 类型
            import mimetypes

            content_type, _ = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = "application/octet-stream"

            # 上传文件
            self.client.fput_object(
                bucket_name=bucket_name,
                object_name=object_name,
                file_path=file_path,
                content_type=content_type,
            )

            logger.info(f"文件上传成功: {bucket_name}/{object_name}")

            return {
                "success": True,
                "bucket_name": bucket_name,
                "object_name": object_name,
                "file_size": file_size,
                "content_type": content_type,
                "original_path": file_path,
            }

        except Exception as e:
            logger.error(f"上传文件失败: {e}")
            return {"success": False, "error": str(e)}

    def upload_bytes(
        self,
        data: bytes,
        filename: str,
        bucket_name: str = None,
        folder: str = None,
        content_type: str = "application/octet-stream",
    ) -> dict:
        """
        上传字节数据到 MinIO

        Args:
            data: 字节数据
            filename: 文件名
            bucket_name: 存储桶名称
            folder: 文件夹路径（可选）
            content_type: MIME 类型

        Returns:
            上传结果字典
        """
        bucket_name = bucket_name or settings.MINIO_BUCKET

        try:
            # 确保存储桶存在
            if not self.ensure_bucket(bucket_name):
                return {"success": False, "error": "存储桶创建失败"}

            # 生成对象名称
            object_name = self._generate_object_name(filename, folder)

            # 上传数据
            self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=io.BytesIO(data),
                length=len(data),
                content_type=content_type,
            )

            logger.info(f"数据上传成功: {bucket_name}/{object_name}")

            return {
                "success": True,
                "bucket_name": bucket_name,
                "object_name": object_name,
                "file_size": len(data),
                "content_type": content_type,
            }

        except Exception as e:
            logger.error(f"上传数据失败: {e}")
            return {"success": False, "error": str(e)}

    # ==================== 文件下载和 URL ====================

    def get_presigned_url(
        self,
        object_name: str,
        bucket_name: str = None,
        expires: int = 7,
        download_filename: str = None,
        force_download: bool = True,
    ) -> str | None:
        """
        生成预签名下载 URL

        Args:
            object_name: 对象名称
            bucket_name: 存储桶名称
            expires: 过期时间
            download_filename: 下载时的文件名（可选）
            force_download: 是否强制下载

        Returns:
            预签名 URL
        """
        bucket_name = bucket_name or settings.MINIO_BUCKET

        try:
            # 设置响应头
            response_headers = {}

            # 强制下载：覆盖 content-type
            if force_download:
                response_headers["response-content-type"] = "application/octet-stream"

            if download_filename:
                import urllib.parse

                # 从 object_name 提取扩展名
                original_ext = Path(object_name).suffix

                # 如果 download_filename 没有扩展名，自动添加
                if not Path(download_filename).suffix and original_ext:
                    download_filename = f"{download_filename}{original_ext}"

                encoded_filename = urllib.parse.quote(download_filename)
                response_headers[
                    "response-content-disposition"
                ] = f"attachment; filename*=UTF-8''{encoded_filename}"

            # 生成预签名 URL
            url = self.client.presigned_get_object(
                bucket_name=bucket_name,
                object_name=object_name,
                expires=timedelta(days=expires),
                response_headers=response_headers if response_headers else None,
            )

            logger.info(f"生成预签名 URL: {object_name}, 有效期 {expires}天")

            # 如果配置了使用 HTTPS URL，转换协议
            if settings.MINIO_USE_HTTPS_URL:
                url = self._convert_to_https(url)

            return url

        except Exception as e:
            logger.error(f"生成预签名 URL 失败: {e}")
            return None

    def get_presigned_url_for_audio(
        self, object_name: str, expires_hours: int = None
    ) -> str:
        """
        生成音频文件的预签名URL（专门用于模型调用）

        Args:
            object_name: MinIO对象名称
            expires_hours: URL有效期（小时），默认使用配置值

        Returns:
            预签名URL字符串，失败返回空字符串
        """
        try:
            expires = (
                expires_hours
                if expires_hours is not None
                else settings.AUDIO_URL_EXPIRES_HOURS
            )

            # 转换小时为天数（get_presigned_url使用天数）
            expires_days = expires / 24.0 if expires < 24 else expires // 24

            url = self.get_presigned_url(
                object_name=object_name,
                expires=expires_days,
                download_filename=None,  # 不强制下载，允许在线播放
                force_download=False,
            )

            if url:
                logger.info(f"生成音频预签名URL成功: {object_name}, 有效期: {expires}小时")
            else:
                logger.error(f"生成音频预签名URL失败: {object_name}")

            return url

        except Exception as e:
            logger.error(f"生成音频预签名URL异常: {object_name}, {e}")
            return ""

    def get_presigned_urls_batch(
        self, object_names: list[str], expires_hours: int = None
    ) -> list[str]:
        """
        批量生成音频文件的预签名URL

        Args:
            object_names: MinIO对象名称列表
            expires_hours: URL有效期（小时），默认使用配置值

        Returns:
            预签名URL列表（失败的返回空字符串）
        """
        urls = []

        for object_name in object_names:
            url = self.get_presigned_url_for_audio(
                object_name=object_name, expires_hours=expires_hours
            )
            urls.append(url)

        success_count = sum(1 for url in urls if url)
        logger.info(f"批量生成音频URL完成: 总数={len(object_names)}, 成功={success_count}")

        return urls

    def download_file(
        self, object_name: str, file_path: str, bucket_name: str = None
    ) -> bool:
        """
        下载文件到本地（可选功能，主要用预签名 URL）

        Args:
            object_name: 对象名称
            file_path: 本地保存路径
            bucket_name: 存储桶名称

        Returns:
            是否成功
        """
        bucket_name = bucket_name or settings.MINIO_BUCKET

        try:
            # 创建保存目录
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # 下载文件
            self.client.fget_object(
                bucket_name=bucket_name, object_name=object_name, file_path=file_path
            )

            logger.info(f"文件下载成功: {object_name} -> {file_path}")
            return True

        except Exception as e:
            logger.error(f"下载文件失败: {e}")
            return False

    # ==================== 文件管理 ====================

    def file_exists(self, object_name: str, bucket_name: str = None) -> bool:
        """
        检查文件是否存在

        Args:
            object_name: 对象名称
            bucket_name: 存储桶名称

        Returns:
            是否存在
        """
        bucket_name = bucket_name or settings.MINIO_BUCKET

        try:
            self.client.stat_object(bucket_name, object_name)
            return True
        except Exception as e:
            logger.error(f"检查文件失败: {e}")
            return False

    def delete_file(self, object_name: str, bucket_name: str = None) -> bool:
        """
        删除文件

        Args:
            object_name: 对象名称
            bucket_name: 存储桶名称

        Returns:
            是否成功
        """
        bucket_name = bucket_name or settings.MINIO_BUCKET

        try:
            self.client.remove_object(bucket_name, object_name)
            logger.info(f"文件删除成功: {bucket_name}/{object_name}")
            return True
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            return False

    def _convert_to_https(self, url):
        """
        转换 URL 为 HTTPS

        Args:
            url: URL

        Returns:
            转换后的 URL
        """
        external_url = url.replace(
            f"http://{settings.MINIO_ENDPOINT}",
            f"https://{settings.MINIO_ENDPOINT.split(':')[0]}/minio",
        )
        return external_url

    # ==================== 分片上传支持 ====================

    def initiate_multipart_upload(
        self,
        object_name: str,
        bucket_name: str = None,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        初始化分片上传

        Args:
            object_name: 对象名称
            bucket_name: 存储桶名称
            content_type: MIME类型

        Returns:
            upload_id: 上传会话ID
        """
        bucket_name = bucket_name or settings.MINIO_BUCKET

        try:
            # 确保存储桶存在
            if not self.ensure_bucket(bucket_name):
                raise Exception("存储桶创建失败")

            # 初始化分片上传
            upload_id = self.client._create_multipart_upload(
                bucket_name=bucket_name,
                object_name=object_name,
                headers={"Content-Type": content_type},
            )

            logger.info(f"初始化分片上传成功: {object_name}, upload_id={upload_id}")
            return upload_id

        except Exception as e:
            logger.error(f"初始化分片上传失败: {e}")
            raise

    def upload_part(
        self,
        object_name: str,
        upload_id: str,
        part_number: int,
        data: bytes,
        bucket_name: str = None,
    ) -> str:
        """
        上传单个分片

        Args:
            object_name: 对象名称
            upload_id: 上传会话ID
            part_number: 分片编号（从1开始）
            data: 分片数据
            bucket_name: 存储桶名称

        Returns:
            etag: 分片标识
        """
        bucket_name = bucket_name or settings.MINIO_BUCKET

        # 转换为 BytesIO 并获取长度
        data_length = len(data)

        try:
            # 上传分片
            etag = self.client._upload_part(
                bucket_name=bucket_name,
                object_name=object_name,
                upload_id=upload_id,
                part_number=part_number,
                data=data,
                headers={"Content-Length": str(data_length)},
            )

            logger.info(f"分片上传成功: part {part_number}, etag={etag}")
            return etag

        except Exception as e:
            logger.error(f"分片上传失败: part {part_number}, {e}")
            raise

    def complete_multipart_upload(
        self, object_name: str, upload_id: str, parts: list, bucket_name: str = None
    ) -> bool:
        """
        完成分片上传

        Args:
            object_name: 对象名称
            upload_id: 上传会话ID
            parts: 分片列表 [{"part_number": 1, "etag": "xxx"}, ...]
            bucket_name: 存储桶名称

        Returns:
            是否成功
        """
        bucket_name = bucket_name or settings.MINIO_BUCKET

        try:
            minio_parts = [Part(part["part_number"], part["etag"]) for part in parts]

            # 完成分片上传
            self.client._complete_multipart_upload(
                bucket_name=bucket_name,
                object_name=object_name,
                upload_id=upload_id,
                parts=minio_parts,
            )

            logger.info(f"完成分片上传: {object_name}")
            return True

        except Exception as e:
            logger.error(f"完成分片上传失败: {e}")
            raise

    def abort_multipart_upload(
        self, object_name: str, upload_id: str, bucket_name: str = None
    ) -> bool:
        """
        取消分片上传

        Args:
            object_name: 对象名称
            upload_id: 上传会话ID
            bucket_name: 存储桶名称

        Returns:
            是否成功
        """
        bucket_name = bucket_name or settings.MINIO_BUCKET

        try:
            self.client._abort_multipart_upload(
                bucket_name=bucket_name, object_name=object_name, upload_id=upload_id
            )

            logger.info(f"取消分片上传: {object_name}")
            return True

        except Exception as e:
            logger.error(f"取消分片上传失败: {e}")
            return False


# 全局单例
minio_client = MinioClient()
