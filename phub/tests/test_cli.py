import os
import sys
import pytest
from unittest.mock import patch, AsyncMock

from phub.phub import run_main, Client

@pytest.mark.asyncio
async def test_cli_download_video(tmp_path):
    test_url = "https://www.pornhub.com/view_video.php?viewkey=ph12345678"
    
    with patch("phub.phub.Client") as MockClient:
        mock_video = AsyncMock()
        mock_video.video_id = "ph12345678"
        
        mock_client_instance = MockClient.return_value
        # Since get_video is an async function, we mock it with an AsyncMock 
        # or just let it return the mock_video directly
        mock_client_instance.get_video = AsyncMock(return_value=mock_video)
        
        output_dir = str(tmp_path)
        test_args = [
            "phub.py", 
            "--download", test_url,
            "--quality", "best",
            "--output", output_dir,
            "--no-title", "False"
        ]
        
        with patch.object(sys, "argv", test_args):
            await run_main()
            
        mock_client_instance.get_video.assert_called_once_with(test_url)
        mock_video.download.assert_called_once_with(quality="best", path=output_dir, no_title=False)


@pytest.mark.asyncio
async def test_cli_id_as_title(tmp_path):
    test_url = "https://www.pornhub.com/view_video.php?viewkey=ph12345678"
    
    with patch("phub.phub.Client") as MockClient:
        mock_video = AsyncMock()
        mock_video.video_id = "ph12345678"
        
        mock_client_instance = MockClient.return_value
        mock_client_instance.get_video = AsyncMock(return_value=mock_video)
        
        output_dir = str(tmp_path)
        test_args = [
            "phub.py", 
            "--download", test_url,
            "--quality", "best",
            "--output", output_dir,
            "--no-title", "False",
            "--id-as-title"
        ]
        
        with patch.object(sys, "argv", test_args):
            await run_main()
            
        expected_path = os.path.join(output_dir, "ph12345678.mp4")
        mock_video.download.assert_called_once_with(quality="best", path=expected_path, no_title=True)



@pytest.mark.asyncio
async def test_cli_iterable_limit(tmp_path):
    test_url = "https://www.pornhub.com/users/testuser"
    
    with patch("phub.phub.Client") as MockClient:
        mock_client_instance = MockClient.return_value
        
        mock_user = AsyncMock()
        mock_client_instance.get_user = AsyncMock(return_value=mock_user)
        
        mock_v1 = AsyncMock()
        mock_v2 = AsyncMock()
        mock_v3 = AsyncMock()
        
        async def mock_get_videos(pages=1):
            yield mock_v1
            yield mock_v2
            yield mock_v3
            
        mock_user.get_videos = mock_get_videos
        
        output_dir = str(tmp_path)
        test_args = [
            "phub.py", 
            "--download", test_url,
            "--quality", "half",
            "--output", output_dir,
            "--no-title", "True",
            "--limit", "2"
        ]
        
        with patch.object(sys, "argv", test_args):
            await run_main()
            
        mock_client_instance.get_user.assert_called_once_with(test_url)
        mock_v1.download.assert_called_once()
        mock_v2.download.assert_called_once()
        mock_v3.download.assert_not_called()
