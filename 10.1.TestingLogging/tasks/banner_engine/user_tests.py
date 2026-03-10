import typing
import random

import pytest

from banner_engine import (
    BannerStat, Banner, BannerStorage, EmptyBannerStorageError, EpsilonGreedyBannerEngine
)
TEST_DEFAULT_CTR = 0.1


@pytest.fixture(scope="function")
def test_banners() -> list[Banner]:
    return [
        Banner("b1", cost=1, stat=BannerStat(10, 20)),
        Banner("b2", cost=250, stat=BannerStat(20, 20)),
        Banner("b3", cost=100, stat=BannerStat(0, 20)),
        Banner("b4", cost=100, stat=BannerStat(1, 20)),
    ]


@pytest.mark.parametrize("clicks, shows, expected_ctr", [(1, 1, 1.0), (20, 100, 0.2), (5, 100, 0.05)])
def test_banner_stat_ctr_value(clicks: int, shows: int, expected_ctr: float) -> None:
    ctr = BannerStat(clicks=clicks, shows=shows).compute_ctr(TEST_DEFAULT_CTR)
    assert ctr == expected_ctr


def test_empty_stat_compute_ctr_returns_default_ctr() -> None:
    ctr = BannerStat(clicks=0, shows=0).compute_ctr(TEST_DEFAULT_CTR)
    assert ctr == TEST_DEFAULT_CTR
    ctr = BannerStat(clicks=0, shows=0).compute_ctr(20.0)
    assert ctr == 20.0


def impl_test_banner_stat_add_show_lowers_ctr(clicks: int, shows: int) -> None:
    banner_stat = BannerStat(clicks=clicks, shows=shows)
    assert banner_stat.shows == shows
    assert banner_stat.clicks == clicks
    banner_stat.add_show()
    assert banner_stat.shows == shows + 1
    assert banner_stat.clicks == clicks
    assert banner_stat.compute_ctr(TEST_DEFAULT_CTR) <= clicks / shows


def test_banner_stats() -> list[tuple[int, int]]:
    return [(1,2), (1,20), (10, 2), (11, 29), (30, 100000)]

def test_banner_stat_add_show_lowers_ctr() -> None:
    for clck, shw in test_banner_stats():
        impl_test_banner_stat_add_show_lowers_ctr(clicks = clck, shows = shw)


def impl_test_banner_stat_add_click_increases_ctr(clicks: int, shows: int) -> None:
    banner_stat = BannerStat(clicks=clicks, shows=shows)
    assert banner_stat.shows == shows
    assert banner_stat.clicks == clicks
    banner_stat.add_click()
    assert banner_stat.shows == shows
    assert banner_stat.clicks == clicks + 1
    assert banner_stat.compute_ctr(TEST_DEFAULT_CTR) >= clicks / shows

def test_banner_stat_add_click_increases_ctr() -> None:
    for clck, shw in test_banner_stats():
        impl_test_banner_stat_add_click_increases_ctr(clicks = clck, shows = shw)


def test_get_banner_with_highest_cpc_returns_banner_with_highest_cpc(test_banners: list[Banner]) -> None:
    storage = BannerStorage(test_banners)
    test_banner = storage.banner_with_highest_cpc()
    test_cpc = test_banner.stat.compute_ctr(TEST_DEFAULT_CTR)
    for banner in test_banners:
        assert test_cpc >= banner.stat.compute_ctr(TEST_DEFAULT_CTR)




def test_banner_engine_raise_empty_storage_exception_if_constructed_with_empty_storage() -> None:
    f = False
    try:
        banner = BannerStorage([])
        EpsilonGreedyBannerEngine(banner, TEST_DEFAULT_CTR)
    except EmptyBannerStorageError:
        f = True
        pass
    assert f

def test_random_names() -> list[str]:
    return ["GOLOVACHEV","GOLOVACHEV2","GOLOVACHEV3", "GOLOVACHEV4", "GOLOVACHEV5",
            "DIMAMALOV1"]


def test_engine_send_click_not_fails_on_unknown_banner(test_banners: list[Banner]) -> None:
    engine = EpsilonGreedyBannerEngine(BannerStorage(test_banners), TEST_DEFAULT_CTR)
    for name in test_random_names():
        engine.send_click(name)


def test_engine_with_zero_random_probability_shows_banner_with_highest_cpc(test_banners: list[Banner]) -> None:
    engine = EpsilonGreedyBannerEngine(BannerStorage(test_banners), 0)
    for _ in range(10):
        assert engine.show_banner() == "b2"


@pytest.mark.parametrize("expected_random_banner", ["b1", "b2", "b3", "b4"])
def test_engine_with_1_random_banner_probability_gets_random_banner(
        expected_random_banner: str,
        test_banners: list[Banner],
        monkeypatch: typing.Any
        ) -> None:
    engine = EpsilonGreedyBannerEngine(BannerStorage(test_banners), 1)
    monkeypatch.setattr(random, "choice", lambda x: expected_random_banner) # TODO: how it works

    assert engine.show_banner() == expected_random_banner


def test_total_cost_equals_to_cost_of_clicked_banners(test_banners: list[Banner]) -> None:
    storage = BannerStorage(test_banners)
    engine = EpsilonGreedyBannerEngine(storage, 0.5)
    sum = 0
    for _ in range(500):
        banner = engine.show_banner()
        if banner == "b1":
            sum += storage.get_banner("b1").cost
        elif banner == "b2":
            sum += storage.get_banner("b2").cost
        elif banner == "b3":
            sum += storage.get_banner("b3").cost
        elif banner == "b4":
            sum += storage.get_banner("b4").cost
        engine.send_click(banner)

    assert engine.total_cost == sum


def test_engine_show_increases_banner_show_stat(test_banners: list[Banner]) -> None:
    storage = BannerStorage(test_banners)
    engine = EpsilonGreedyBannerEngine(storage, 0)
    initial_shows = storage.get_banner("b2").stat.shows

    engine.show_banner()
    assert storage.get_banner("b2").stat.shows == initial_shows + 1
    engine.show_banner()
    assert storage.get_banner("b2").stat.shows == initial_shows + 2


def test_engine_click_increases_banner_click_stat(test_banners: list[Banner]) -> None:
    storage = BannerStorage(test_banners)
    engine = EpsilonGreedyBannerEngine(storage,TEST_DEFAULT_CTR)
    last_click = storage.get_banner("b1").stat.clicks
    for i in range(1, 1000):
        engine.send_click("b1")
        last_click += 1
        assert last_click == storage.get_banner("b1").stat.clicks
