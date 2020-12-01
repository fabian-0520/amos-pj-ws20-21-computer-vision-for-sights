from crawler.main import AutoCrawler
import argparse
from .sight_collector import get_sights

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip",
        type=str,
        default="true",
        help="Skips keyword already downloaded before. This is needed when re-downloading.",
    )
    parser.add_argument("--threads", type=int, default=4, help="Number of threads to download.")
    parser.add_argument("--google", type=str, default="true", help="Download from google.com (boolean)")
    parser.add_argument(
        "--full", type=str, default="false", help="Download full resolution image instead of thumbnails (slow)"
    )
    parser.add_argument("--face", type=str, default="false", help="Face search mode")
    parser.add_argument(
        "--no_gui",
        type=str,
        default="auto",
        help="No GUI mode. Acceleration for full_resolution mode. "
        "But unstable on thumbnail mode. "
        'Default: "auto" - false if full=false, true if full=true',
    )
    parser.add_argument(
        "--limit", type=int, default=0, help="Maximum count of images to download per site. (0: infinite)"
    )
    parser.add_argument(
        "--no_driver",
        type=str,
        default="false",
        help="Whether a preconfigured driver should not be used (by default false, meaning it will)",
    )
    parser.add_argument("--region", type=str, default="Berlin", help="The region sights need to be found for")
    parser.add_argument(
        "--sights_limit", type=int, default=10, help="The limit of sights to be found by the collector api"
    )
    args = parser.parse_args()

    _skip = False if str(args.skip).lower() == "false" else True
    _threads = args.threads
    _google = False if str(args.google).lower() == "false" else True
    _full = False if str(args.full).lower() == "false" else True
    _no_driver = True if str(args.no_driver).lower() == "true" else False
    _face = False if str(args.face).lower() == "false" else True
    _limit = int(args.limit)
    _region = args.region
    _sights_limit = args.sights_limit

    no_gui_input = str(args.no_gui).lower()
    if no_gui_input == "auto":
        _no_gui = _full
    elif no_gui_input == "true":
        _no_gui = True
    else:
        _no_gui = False

    print(
        "Options - skip:{}, threads:{}, google:{}, full_resolution:{}, face:{}, no_gui:{}, limit:{}, region:{}, "
        "no_driver:{}, sights_limit:{} ".format(
            _skip, _threads, _google, _full, _face, _no_gui, _limit, _region, _no_driver, _sights_limit
        )
    )

    sights = get_sights(region=_region, sights_limit=_sights_limit)
    print(f"Sights: {sights}")
    crawler = AutoCrawler(
        skip_already_exist=_skip,
        n_threads=_threads,
        do_google=_google,
        full_resolution=_full,
        face=_face,
        no_gui=_no_gui,
        limit=_limit,
        keyword_list=sights,
        no_driver=_no_driver,
    )
    crawler.do_crawling()
