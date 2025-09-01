import requests


headers = {
    # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Cookie": "PHPSESSID=t51j782oc2kkc8n6kbtqvbar2f; qm_check=A1sdRUIQChtxen8pI0dAOQkKWVIeEHh+c3QgRioNDBgWFWVXXl1VRl0XXEcpCAkWUBd/ARlgRldJRjIGCwkfVl5UWVxUFG4AFBQBFxdTFxsQU1FVV1NHXEVYVElWBRsCHAkSSQ%3D%3D; gr_user_id=a2e999f8-3fde-491e-8354-17846e32309e; USERINFO=gvBSDJSp1V%2BqAuscmeLGQIi1iYmPgSgTepN1LgYK67p2ouZxRLiTCHIKhwt1CmnwwnUd4P6QVqRj7ROWUIq0W0sTCy2oork66KahCIZHhpvYBrvgVmltweGp0uu4DbQ1D2LcajvkK3qTGlzyYxJYeA%3D%3D; ada35577182650f1_gr_last_sent_cs1=qm25605038842; aso_ucenter=ef22aj8Qme%2FOdHfKg9Feu%2F%2FjQdC9RTcHKu8h1IKKW7%2FtOgz0KrDF0COgc8FDwgFY9Lo; AUTHKEY=NRWvkiIYnmW0KOyAxVY8mCoEP3fCMPfHNVSFh9Y6Jx%2FM39rb0UK%2FIkl1y1K6Axe%2FJ8QC%2BjtYrScgZ69bQlCwNeNae4cdyuscNh80TAoG9B%2FINUWZWiQ1Ig%3D%3D; synct=1756050592.920; syncd=-27; ada35577182650f1_gr_cs1=qm25605038842",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
}
res = requests.get("https://api.qimai.cn/rank/indexPlus/brand_id/2?brand=all&country=cn&device=iphone&date=2024-08-25&page=1&genre=36", headers=headers)
print(res.text)