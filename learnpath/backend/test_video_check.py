#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(__file__))

from assessments.dynamic_resource_fetcher import DynamicResourceFetcher

def test_video_availability():
    fetcher = DynamicResourceFetcher()

    # Test the problematic URL
    test_url = 'https://www.youtube.com/watch?v=hKB1sLHwWME'
    result = fetcher._check_video_url_availability(test_url)

    print(f"Testing URL: {test_url}")
    print(f"Availability check result: {result}")

    # Test a known working URL
    working_url = 'https://www.youtube.com/watch?v=PkZNo7MFNFg'  # JavaScript Fundamentals video
    result2 = fetcher._check_video_url_availability(working_url)

    print(f"Testing working URL: {working_url}")
    print(f"Availability check result: {result2}")

if __name__ == "__main__":
    test_video_availability()
