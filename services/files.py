import uuid
from typing import List

import boto3
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from db.models import FileModel
from settings import get_settings
from schemas.types import FileType


async def get_files(session: AsyncSession) -> List[FileType]:
    ''' Getting list of files '''

    query = select(FileModel).options(joinedload('*'))
    result = await session.execute(query)
    return result.scalars().unique().all()


async def upload(file: UploadFile, session: AsyncSession) -> FileType:
    ''' Uploading files to AWS S3 '''

    S3_BUCKET_NAME = get_settings().s3_bucket

    # Uploading
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(S3_BUCKET_NAME)
    path = f'media/{uuid.uuid4().hex[:12]}_{file.filename}'
    bucket.upload_fileobj(file.file, path, ExtraArgs={'ACL': 'public-read'})
    uploaded_file_url = f'https://{S3_BUCKET_NAME}.s3.amazonaws.com/{path}'

    # Storing URL in database
    added_file = FileModel(
        file_name=file.filename,
        file_url=uploaded_file_url
    )
    session.add(added_file)
    await session.commit()

    return added_file
