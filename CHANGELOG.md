## [v3.4.1](https://github.com/edm-su/api/compare/997d4219c886b6b6082eccb8f57b17a4834bca9d..v3.4.1) - 2024-08-19
#### Bug Fixes
- **(deps)** bump sqlalchemy from 2.0.28 to 2.0.32 (#616) - ([8dc32f2](https://github.com/edm-su/api/commit/8dc32f26db1561b773118afece6687d011588424)) - dependabot[bot]
- **(deps)** bump ruff from 0.5.4 to 0.6.1 (#613) - ([2f9f0c1](https://github.com/edm-su/api/commit/2f9f0c10248debe429c2fde08bbf00ec5a027b20)) - dependabot[bot]
- **(deps)** bump aiohttp from 3.9.5 to 3.10.3 (#611) - ([f4cdd51](https://github.com/edm-su/api/commit/f4cdd512467439ae0ffca52273d0a29d4a744b80)) - dependabot[bot]
- **(deps)** bump ruff from 0.5.2 to 0.5.4 (#601) - ([9f53b51](https://github.com/edm-su/api/commit/9f53b51b90159a49c4fc9a8f11dc4d07da1d5846)) - dependabot[bot]
- **(deps)** bump mypy from 1.9.0 to 1.11.0 (#600) - ([86cca6b](https://github.com/edm-su/api/commit/86cca6b3af288001b8be0543f8040c4ee1bf78ee)) - dependabot[bot]
- **(deps)** bump aioboto3 from 13.0.1 to 13.1.1 (#596) - ([11b4d04](https://github.com/edm-su/api/commit/11b4d041ef40730061094463aad00d32776834a9)) - dependabot[bot]
- **(deps)** bump setuptools from 69.0.2 to 70.0.0 (#595) - ([997d421](https://github.com/edm-su/api/commit/997d4219c886b6b6082eccb8f57b17a4834bca9d)) - dependabot[bot]
#### Build system
- replace release-please to cog (#620) - ([92771fd](https://github.com/edm-su/api/commit/92771fd634f0889b9fb6bb3ba062ebf68c4e0eb5)) - Egor Gluhih
- migrate to uv (#619) - ([9696975](https://github.com/edm-su/api/commit/9696975a26f01ce05a6af5dce47d9db29c84b88a)) - Egor Gluhih
- update poetry version in pre-commit hook (#614) - ([44bfee8](https://github.com/edm-su/api/commit/44bfee88a5f6cb408301a4fa6353516d2d75e0f6)) - Egor Gluhih

- - -
## [v3.7.0](https://github.com/edm-su/api/compare/9829c314e8ee3371c51ef0c1ac1ba87e6fe42ec7..v3.7.0) - 2025-01-27
#### Bug Fixes
- **(deps)** update dependency pillow to >=11.1.0,<11.2.0 - ([dda4acc](https://github.com/edm-su/api/commit/dda4accd24b7920efdb0bcbaeb4b0d143b83693c)) - renovate[bot]
- **(deps)** update dependency fastapi to v0.115.6 - ([2477836](https://github.com/edm-su/api/commit/24778361f25c02b571b4e03bc641ed476e2fcc08)) - renovate[bot]
- **(deps)** update dependency pydantic to ~=2.10.1 (#673) - ([cc7b898](https://github.com/edm-su/api/commit/cc7b898493374194ce283496c396f1797d35d3ae)) - renovate[bot]
- **(deps)** update dependency fastapi to v0.115.5 (#663) - ([7fdae0e](https://github.com/edm-su/api/commit/7fdae0e5dcb93dd3f105c6faf290d97a46fdb30c)) - renovate[bot]
- **(deps)** update dependency aiofiles to v24 (#656) - ([5e300a1](https://github.com/edm-su/api/commit/5e300a1ff2ac25b9aaa1e6d59036a4c252458da4)) - renovate[bot]
- **(deps)** update dependency authzed to >=1.1.0,<2.0.0 (#657) - ([030c07e](https://github.com/edm-su/api/commit/030c07e30bcde0c40edb1e76a4a15fcd2b88f09b)) - renovate[bot]
- **(deps)** update dependency pillow to v11 (#658) - ([a54d93b](https://github.com/edm-su/api/commit/a54d93ba49c04ff2f1fb200812f8eca2b92a275d)) - renovate[bot]
- **(deps)** update dependency meilisearch-python-async to v1.8.1 (#648) - ([cb067b1](https://github.com/edm-su/api/commit/cb067b19ad9b034b0547ada42838bf4fee478f7e)) - renovate[bot]
- **(deps)** update dependency fastapi to v0.115.4 (#647) - ([ec0b969](https://github.com/edm-su/api/commit/ec0b969ffa8fb75e8dca69781bfc02c26a396812)) - renovate[bot]
- video slug generator (#671) - ([a27c2a0](https://github.com/edm-su/api/commit/a27c2a09431ca62fc297b1a46692c03b9ab875cb)) - Egor Gluhih
#### Build system
- migrate docker build actions to native arm64 (#676) - ([ba05042](https://github.com/edm-su/api/commit/ba05042a046774d1fbc0a5bbc727744a5bcf13f2)) - Egor Gluhih
#### Continuous Integration
- change automerge type - ([12075b9](https://github.com/edm-su/api/commit/12075b91c90a3be4489802326f69af7c48cd96b4)) - Egor Gluhih
- fix automerge config - ([41b006a](https://github.com/edm-su/api/commit/41b006ac196ff89b5c0d8d763ba5c84ee78f508d)) - Egor Gluhih
- migrate to renovate - ([43f87fe](https://github.com/edm-su/api/commit/43f87fedcc82225078cc912426a83a85f7006be8)) - Egor Gluhih
- add 3.13 python (#641) - ([3e355f9](https://github.com/edm-su/api/commit/3e355f9cdf42312d289de9c290a511cdd8b656fe)) - Egor Gluhih
- correct coverage path in test workflow (#640) - ([45c6d92](https://github.com/edm-su/api/commit/45c6d925b6731988b94a158bf0dde5bbe40cd76e)) - Egor Gluhih
#### Features
- add is blocked in Russia flag (#677) - ([eee6b95](https://github.com/edm-su/api/commit/eee6b95ab3b2a02de562babee5d3abb0866e79d6)) - Egor Gluhih
-  add is favorite video attribute (#675) - ([b2bb3be](https://github.com/edm-su/api/commit/b2bb3be0684994613b7237a967f21b422ea409dd)) - Egor Gluhih
- remove deprecated functionality - ([0c5289c](https://github.com/edm-su/api/commit/0c5289c933351822129a33b43c99eed8a40f1838)) - Egor Gluhih
- remove min_length constraint from annotation field - ([979c3a6](https://github.com/edm-su/api/commit/979c3a6242cc2a0c6249874f3f0bb831fe68ae58)) - Egor Gluhih
#### Miscellaneous Chores
- **(deps)** update getmeili/meilisearch docker tag to v1.12.6 - ([d34466d](https://github.com/edm-su/api/commit/d34466d77c9966bf8cacc9edd00c0b0ee416d3d5)) - renovate[bot]
- **(deps)** update dependency pre-commit to >=4.1.0,<4.2.0 - ([a6fb1a8](https://github.com/edm-su/api/commit/a6fb1a81dce5f84d37f69333548ba12f3e82f11d)) - renovate[bot]
- **(deps)** update getmeili/meilisearch docker tag to v1.12.5 - ([26217ab](https://github.com/edm-su/api/commit/26217aba3d632cdb95f212087a3b32644a430979)) - renovate[bot]
- **(deps)** lock file maintenance - ([2fe43de](https://github.com/edm-su/api/commit/2fe43de93a2c9f1dafd0a8d6e3af62c53d65e9bf)) - renovate[bot]
- **(deps)** update pre-commit hook charliermarsh/ruff-pre-commit to v0.9.2 - ([8cba0b0](https://github.com/edm-su/api/commit/8cba0b061eedfedfe7859942199dbc1349f71a34)) - renovate[bot]
- **(deps)** update getmeili/meilisearch docker tag to v1.12.4 - ([d4562df](https://github.com/edm-su/api/commit/d4562dfc1b7416c07574ef528d0dc27819f0ac86)) - renovate[bot]
- **(deps)** update getmeili/meilisearch docker tag to v1.12.3 - ([cb40b22](https://github.com/edm-su/api/commit/cb40b2294c2a9154b65b6576e46440cbe50f1c73)) - renovate[bot]
- **(deps)** lock file maintenance - ([cfb3195](https://github.com/edm-su/api/commit/cfb3195c865f85856e36ad37fe7b3300fdd3c971)) - renovate[bot]
- **(deps)** update pre-commit hook charliermarsh/ruff-pre-commit to v0.9.1 - ([4eaa156](https://github.com/edm-su/api/commit/4eaa15632f58cfb7ce0e7730ef899aa06da5449e)) - renovate[bot]
- **(deps)** update pre-commit hook charliermarsh/ruff-pre-commit to v0.9.0 - ([9528f0d](https://github.com/edm-su/api/commit/9528f0d8fd0d37eb82c32a7611531d72225a4039)) - renovate[bot]
- **(deps)** update dependency ruff to >=0.9.0,<0.10.0 - ([b077aa1](https://github.com/edm-su/api/commit/b077aa1b1a4d6fc665f275c1861dfae9440f8d97)) - renovate[bot]
- **(deps)** update getmeili/meilisearch docker tag to v1.12.2 - ([1e644d0](https://github.com/edm-su/api/commit/1e644d04c79e2587a4820da2af8891233cf23714)) - renovate[bot]
- **(deps)** lock file maintenance - ([9853d46](https://github.com/edm-su/api/commit/9853d4668f5a98f732abd70b2aec292b9eb8fec0)) - renovate[bot]
- **(deps)** update pre-commit hook charliermarsh/ruff-pre-commit to v0.8.6 - ([5f31a07](https://github.com/edm-su/api/commit/5f31a07f29929e2de9b36802c843788048d0247c)) - renovate[bot]
- **(deps)** update dependency faker to >=33.3.0,<33.4.0 - ([b44bd41](https://github.com/edm-su/api/commit/b44bd41b63591f08e1ef85c4a6ff033abd0c4ede)) - renovate[bot]
- **(deps)** update pre-commit hook charliermarsh/ruff-pre-commit to v0.8.5 - ([5f12356](https://github.com/edm-su/api/commit/5f12356d4977d02de2ab91c3cd7d3fe2c3c87af0)) - renovate[bot]
- **(deps)** update getmeili/meilisearch docker tag to v1.12.1 - ([86e06fb](https://github.com/edm-su/api/commit/86e06fb96a34dc71f275ba4d8696f6bffffa619f)) - renovate[bot]
- **(deps)** update pre-commit hook pre-commit/mirrors-mypy to v1.14.1 - ([0d2c0e5](https://github.com/edm-su/api/commit/0d2c0e5331592d8512278971e8414d8d81671c18)) - renovate[bot]
- **(deps)** lock file maintenance - ([ab0b8da](https://github.com/edm-su/api/commit/ab0b8da8f9d20af56ad965de37c8e2da7821d1fa)) - renovate[bot]
- **(deps)** update getmeili/meilisearch docker tag to v1.12.0 - ([82bf4e1](https://github.com/edm-su/api/commit/82bf4e10796c3ca6ee410f7f734c73ab84f03c69)) - renovate[bot]
- **(deps)** lock file maintenance - ([92fea16](https://github.com/edm-su/api/commit/92fea16f2fe14cdf5d1e7a59492aa2f924de9662)) - renovate[bot]
- **(deps)** update pre-commit hook pre-commit/mirrors-mypy to v1.14.0 - ([7040feb](https://github.com/edm-su/api/commit/7040feb2b3b1b793010ea7fcc1fd226a0d4fb3ae)) - renovate[bot]
- **(deps)** update pre-commit hook compilerla/conventional-pre-commit to v4 - ([acdb734](https://github.com/edm-su/api/commit/acdb734f44f82415944ace0824b17e54e3b24a73)) - renovate[bot]
- **(deps)** update pre-commit hook charliermarsh/ruff-pre-commit to v0.8.4 - ([77acb5c](https://github.com/edm-su/api/commit/77acb5c57d80958dccd2e3a4a1127efb6886fae5)) - renovate[bot]
- **(deps)** lock file maintenance - ([f95f7f8](https://github.com/edm-su/api/commit/f95f7f83cb7fed2bf58733251cb2c73060bb509a)) - renovate[bot]
- **(deps)** update pre-commit hook charliermarsh/ruff-pre-commit to v0.8.3 - ([c17013f](https://github.com/edm-su/api/commit/c17013f7d9a85a97161b6de4b50b1bfbbd39a19d)) - renovate[bot]
- **(deps)** lock file maintenance - ([f211863](https://github.com/edm-su/api/commit/f21186398997c5be3ed8398de7775c872f4661e3)) - renovate[bot]
- **(deps)** update pre-commit hook charliermarsh/ruff-pre-commit to v0.8.2 - ([d551ba0](https://github.com/edm-su/api/commit/d551ba06325c26939a673c9d30a366de086b6c02)) - renovate[bot]
- **(deps)** update python docker tag to v3.13.1 - ([7d6a1ec](https://github.com/edm-su/api/commit/7d6a1ec6882d756bd062b0b6503c43d35027c077)) - renovate[bot]
- **(deps)** lock file maintenance - ([eeda97b](https://github.com/edm-su/api/commit/eeda97b94e60172b4ee397ea5555be1e9f8f9f2c)) - renovate[bot]
- **(deps)** update pre-commit hook charliermarsh/ruff-pre-commit to v0.8.1 - ([de2e876](https://github.com/edm-su/api/commit/de2e876b36e91227630925cc46ad4b281448a827)) - renovate[bot]
- **(deps)** update dependency faker to >=33.1.0,<33.2.0 - ([5f447cc](https://github.com/edm-su/api/commit/5f447cc91f64fb40b8e15c3a9c33035c996d609f)) - renovate[bot]
- **(deps)** lock file maintenance - ([cb94b8d](https://github.com/edm-su/api/commit/cb94b8d03589908869912d722195347a2cf1e32b)) - renovate[bot]
- **(deps)** update pre-commit hook pre-commit/mirrors-mypy to v1.13.0 (#674) - ([9cc1f49](https://github.com/edm-su/api/commit/9cc1f49d65eb6a542032c4c6642cd8621e20321b)) - renovate[bot]
- **(deps)** update pre-commit hook compilerla/conventional-pre-commit to v3.6.0 - ([0d66fb3](https://github.com/edm-su/api/commit/0d66fb37fd7760610e47684e82dc73644b394cd8)) - renovate[bot]
- **(deps)** update pre-commit hook charliermarsh/ruff-pre-commit to v0.8.0 - ([e861f89](https://github.com/edm-su/api/commit/e861f898c74dc68d2ab9f16029abab03faef7c6d)) - renovate[bot]
- **(deps)** update postgres docker tag to v17.2 - ([ed3fd6a](https://github.com/edm-su/api/commit/ed3fd6ad96019219767e836f5286b69a89a43cf1)) - renovate[bot]
- **(deps)** update dependency ruff to >=0.8.0,<0.9.0 - ([e2b6391](https://github.com/edm-su/api/commit/e2b63918fd53035591d7dfee551840c45a2f1c20)) - renovate[bot]
- **(deps)** lock file maintenance - ([41f28fe](https://github.com/edm-su/api/commit/41f28feac8fdd0754a5a7d02b6a80c4c4ea3b916)) - renovate[bot]
- **(deps)** lock file maintenance (#672) - ([8ff485b](https://github.com/edm-su/api/commit/8ff485bfc360a212dfb210a6c41bcb30a7c6b509)) - renovate[bot]
- **(deps)** update dependency faker to v33 (#667) - ([60665ba](https://github.com/edm-su/api/commit/60665ba57a4cc4215cdb3baa1831e8d0f605f912)) - renovate[bot]
- **(deps)** update codecov/codecov-action action to v5 (#668) - ([e6c12e8](https://github.com/edm-su/api/commit/e6c12e87cf8df436b4eabcc6997ae31f835aebaf)) - renovate[bot]
- **(deps)** update postgres docker tag to v17.1 (#669) - ([b468590](https://github.com/edm-su/api/commit/b468590df4faca8828f7c98102dc98b45cca4c75)) - renovate[bot]
- **(deps)** update getmeili/meilisearch docker tag to v1.11.3 (#666) - ([5dae019](https://github.com/edm-su/api/commit/5dae0190d216f074a9814d24a1a2a23d30034856)) - renovate[bot]
- **(deps)** update dependency faker to v32 (#665) - ([b3204de](https://github.com/edm-su/api/commit/b3204de26e9a9ac0fa06e68d03489c0f916c8bf1)) - renovate[bot]
- **(deps)** update dependency faker to >=30.10.0,<30.11.0 (#664) - ([f782ae4](https://github.com/edm-su/api/commit/f782ae4c8e84c1907c62cc3d3b140387db654611)) - renovate[bot]
- **(deps)** lock file maintenance (#662) - ([01d5c70](https://github.com/edm-su/api/commit/01d5c70fe90df5d4fe1dc88012fd873a5d37123b)) - renovate[bot]
- **(deps)** update getmeili/meilisearch docker tag to v1.11.1 (#659) - ([b0edc91](https://github.com/edm-su/api/commit/b0edc91a5ebe56cb51625dfb04fc7f5a179b9904)) - renovate[bot]
- **(deps)** update dependency types-aiofiles to v24 (#655) - ([4164ed9](https://github.com/edm-su/api/commit/4164ed9ce90e4d6550cdcde673ab719153212534)) - renovate[bot]
- **(deps)** update dependency faker to v30 (#652) - ([68d9da9](https://github.com/edm-su/api/commit/68d9da90998bd05d4b3f5a00c00154a252ece75c)) - renovate[bot]
- **(deps)** update dependency ruff to >=0.7.3,<0.8.0 (#651) - ([ba211dd](https://github.com/edm-su/api/commit/ba211dd1390591c76a22810cc97e0381004f2f25)) - renovate[bot]
- **(deps)** update dependency pre-commit to v4 (#653) - ([9525378](https://github.com/edm-su/api/commit/9525378be7ea078279a10f0347e44fb71960d7b1)) - renovate[bot]
- **(deps)** update dependency pytest-cov to v6 (#654) - ([f81065e](https://github.com/edm-su/api/commit/f81065edb4dfed641bd5c957f7ba26764a8f5dfb)) - renovate[bot]
- **(deps)** update postgres docker tag to v17 (#661) - ([734b8fb](https://github.com/edm-su/api/commit/734b8fbbc3bb9653361c88346a37f8520a19beb1)) - renovate[bot]
- **(deps)** lock file maintenance (#650) - ([8ed6096](https://github.com/edm-su/api/commit/8ed60961dfbdf11062e614b807266e9f813a1d56)) - renovate[bot]
- update pre-commit dependencies - ([2073a52](https://github.com/edm-su/api/commit/2073a522500819cb49c3038cd5615d2aa0f8c2fb)) - Egor Gluhih
- add pre-commit auto-upgrade - ([6459126](https://github.com/edm-su/api/commit/64591267a8eb07e19763fe636c1ea66f2efb377a)) - Egor Gluhih
- bump fastapi[standard] from 0.115.0 to 0.115.3 (#644) - ([519327f](https://github.com/edm-su/api/commit/519327fd703057a73f57211c090814fa9c406a5f)) - dependabot[bot]
- bump python from 3.12.7-slim-bullseye to 3.13.0-slim-bullseye (#638) - ([0b5d02a](https://github.com/edm-su/api/commit/0b5d02a8cfcb2b1f7bdba242bb3cd1dc3a5245cd)) - dependabot[bot]
- update authzed requirement (#635) - ([cca0319](https://github.com/edm-su/api/commit/cca03198fd606df08d853505e2aea2d985b52bde)) - dependabot[bot]
- bump python from 3.12.6-slim-bullseye to 3.12.7-slim-bullseye (#634) - ([9ce2a42](https://github.com/edm-su/api/commit/9ce2a426b50a49b13d690f9dae402f6f01258889)) - dependabot[bot]
#### Refactoring
-  use lifespan event (#636) - ([6ac1ce6](https://github.com/edm-su/api/commit/6ac1ce6f23c3402e0e36534176edbf688e58614d)) - Egor Gluhih
- consolidate post creation logic and update dependencies (#633) - ([9829c31](https://github.com/edm-su/api/commit/9829c314e8ee3371c51ef0c1ac1ba87e6fe42ec7)) - Egor Gluhih
#### Revert
- Back out "build: migrate docker build actions to native arm64 (#676)" - ([908b9fb](https://github.com/edm-su/api/commit/908b9fb45a8081b7ee494ed44f699491d7f7182b)) - [@EgorHenek](https://github.com/EgorHenek)
#### Style
- upgrade ruff config - ([bf5eb04](https://github.com/edm-su/api/commit/bf5eb04657d8dc0a2e6af4a1da69dde1a8a57e6f)) - Egor Gluhih
#### Tests
- replace pytest-asyncio to anyio (#639) - ([daa2b53](https://github.com/edm-su/api/commit/daa2b5371c81d9db9c7441b7c1c4eb082ccea604)) - Egor Gluhih

- - -

## [v3.6.0](https://github.com/edm-su/api/compare/ef3fe239fc58359d8a42643447319bb09477b07f..v3.6.0) - 2024-10-01
#### Features
- add types-aioboto3[s3] dependency to project dependencies - ([ef3fe23](https://github.com/edm-su/api/commit/ef3fe239fc58359d8a42643447319bb09477b07f)) - Egor Gluhih

- - -

## [v3.5.0](https://github.com/edm-su/api/compare/bcd949dd476fe013286aee513839ba66e8cf26f3..v3.5.0) - 2024-10-01
#### Bug Fixes
- **(deps)** bump fastapi[all] from 0.110.0 to 0.112.1 (#621) - ([bcd949d](https://github.com/edm-su/api/commit/bcd949dd476fe013286aee513839ba66e8cf26f3)) - dependabot[bot]
#### Features
- add pre signed url generation for file uploads (#631) - ([64c8e4c](https://github.com/edm-su/api/commit/64c8e4cb4c1f33dbd07b0f7ed7db62fd7286a92a)) - Egor Gluhih
#### Miscellaneous Chores
- bump python from 3.12-slim-bullseye to 3.12.6-slim-bullseye (#628) - ([a81dca7](https://github.com/edm-su/api/commit/a81dca7f7ce33106c79d996e0e32102d2047e3d0)) - dependabot[bot]
- bump fastapi[standard] from 0.114.2 to 0.115.0 (#630) - ([2291f66](https://github.com/edm-su/api/commit/2291f66eb44ef232fd697867bd4f7707943ba253)) - dependabot[bot]
- bump fastapi[standard] from 0.114.1 to 0.114.2 (#629) - ([ee8090f](https://github.com/edm-su/api/commit/ee8090f43d1f9c1a94244fd2860abe6b3e0070dc)) - dependabot[bot]
- bump fastapi[standard] from 0.112.1 to 0.114.1 (#627) - ([881ec04](https://github.com/edm-su/api/commit/881ec0410fea1a4ab3a9fae2dd36f15441385175)) - dependabot[bot]
- update authzed requirement (#624) - ([aae27ea](https://github.com/edm-su/api/commit/aae27eaa3c7eb53b0fc975530e2e5026288d254b)) - dependabot[bot]
- update commit message prefixes in dependabot configuration - ([0c426ab](https://github.com/edm-su/api/commit/0c426ab6980d4b2083de486f087eeb816ecf34b0)) - Egor Gluhih
- add typings to .gitignore - ([718d824](https://github.com/edm-su/api/commit/718d8248f868d42620ef34909b3bc8126e25d28f)) - Egor Gluhih
#### Tests
- update test.yml - ([8538ac1](https://github.com/edm-su/api/commit/8538ac110c2325707a8aab0c826cb89191ed3190)) - Egor Gluhih

- - -


## [v3.4.0](https://github.com/edm-su/api/compare/v3.3.1..v3.4.0) - 2024-08-19
#### Bug Fixes
- **(deps)** bump alembic from 1.13.1 to 1.13.2 (#587) - ([5a5534b](https://github.com/edm-su/api/commit/5a5534b600a591ca79e446bba13c048ade6315d7)) - dependabot[bot]
- **(deps)** bump certifi from 2023.7.22 to 2024.7.4 (#590) - ([3e92c3f](https://github.com/edm-su/api/commit/3e92c3f3c022b353108832c4c84f615246a02695)) - dependabot[bot]
- **(deps)** bump ruff from 0.4.8 to 0.5.2 (#593) - ([b20057d](https://github.com/edm-su/api/commit/b20057da970b0f3a10ee492293edc64946252898)) - dependabot[bot]
- **(deps)** bump typing-extensions from 4.10.0 to 4.12.2 (#567) - ([7a1fd25](https://github.com/edm-su/api/commit/7a1fd25de551b26b131e008d89caea5dd39a7c93)) - dependabot[bot]
- **(deps)** bump pytest from 7.4.4 to 8.2.2 (#569) - ([e006a82](https://github.com/edm-su/api/commit/e006a822d87f9e16886bb1dbeebec2b5ea7b8bd1)) - dependabot[bot]
#### Continuous Integration
- **(actions)** bump docker/build-push-action from 5 to 6 (#578) - ([33ec0b3](https://github.com/edm-su/api/commit/33ec0b38a7efa8530862a6c2d3fc20d53b24bb8b)) - dependabot[bot]
- poetry version has been updated (#574) - ([2964ffc](https://github.com/edm-su/api/commit/2964ffcc110cba81b440853ff5befde13ed5afb4)) - Egor Gluhih
#### Features
- postgres settings are placed in a separate class (#594) - ([f16678c](https://github.com/edm-su/api/commit/f16678c0dfa9d03e59935ca5816a9adf3bbe56dc)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 3.4.0 (#572) - ([b2445e5](https://github.com/edm-su/api/commit/b2445e50b87be26c765b67c10d40aa27d8a26293)) - Egor Gluhih
- removed vscode dir (#573) - ([814c33a](https://github.com/edm-su/api/commit/814c33a03dbddc014c019fbc497477edaafc3e9f)) - Egor Gluhih

- - -

## [v3.3.1](https://github.com/edm-su/api/compare/v3.3.0..v3.3.1) - 2024-08-19
#### Bug Fixes
- **(deps)** bump pytest-cov from 4.1.0 to 5.0.0 (#540) - ([ccc68c3](https://github.com/edm-su/api/commit/ccc68c3e5576733794d92b3ed81e23690ec784f2)) - dependabot[bot]
- **(deps)** bump pytest-httpx from 0.27.0 to 0.30.0 (#522) - ([468ca67](https://github.com/edm-su/api/commit/468ca676d7613aaeef4af61e854f2bf2cf65da9d)) - dependabot[bot]
- **(deps)** bump requests from 2.31.0 to 2.32.2 (#565) - ([25f4b25](https://github.com/edm-su/api/commit/25f4b25d1e603dd7da6db3552437cf2bbfdf78fb)) - dependabot[bot]
- **(deps)** bump pre-commit from 3.6.2 to 3.7.1 (#557) - ([7184558](https://github.com/edm-su/api/commit/71845581d4a31cf96b61b64ff21836d5fde1445e)) - dependabot[bot]
- **(deps)** bump ruff from 0.3.7 to 0.4.8 (#563) - ([a1f40e6](https://github.com/edm-su/api/commit/a1f40e6a0964bb2a8360d0b21ddbaecf8e2a681d)) - dependabot[bot]
- **(deps)** bump aioboto3 from 12.2.0 to 13.0.1 (#564) - ([cefe9d9](https://github.com/edm-su/api/commit/cefe9d9988279ecfbbd34ff8d4ae0710f196a4a2)) - dependabot[bot]
- **(deps)** bump aiohttp from 3.9.3 to 3.9.5 (#549) - ([d462de1](https://github.com/edm-su/api/commit/d462de16770ab47f189ffa251aa6d386db6be658)) - dependabot[bot]
- **(deps)** bump ruff from 0.3.3 to 0.3.7 (#547) - ([28f6303](https://github.com/edm-su/api/commit/28f6303982b1aad4b219166055b3488aed93bf38)) - dependabot[bot]
- **(deps)** bump idna from 3.4 to 3.7 (#546) - ([f46711e](https://github.com/edm-su/api/commit/f46711e0fcf1786895a6846badf9ada1d45d9420)) - dependabot[bot]
- **(deps)** bump dnspython from 2.4.2 to 2.6.1 (#548) - ([7db6e5b](https://github.com/edm-su/api/commit/7db6e5b5a92dab0f47e0d10e7a483265d0f19e08)) - dependabot[bot]
- **(deps)** bump pytest from 7.4.2 to 7.4.4 (#545) - ([d37c522](https://github.com/edm-su/api/commit/d37c5228e150bc18fc6255476ba4b92c89029fbf)) - dependabot[bot]
- **(deps)** bump types-aiofiles from 23.2.0.20240106 to 23.2.0.20240403 (#542) - ([8250b1f](https://github.com/edm-su/api/commit/8250b1fb5c41afe90f08cdff05bd7cb895e6e892)) - dependabot[bot]
- **(deps)** bump pillow from 10.2.0 to 10.3.0 (#543) - ([05f617f](https://github.com/edm-su/api/commit/05f617f8db41e3fb62afbac4371b7b7f1134527d)) - dependabot[bot]
- **(deps)** bump pytest-mock from 3.12.0 to 3.14.0 (#535) - ([cfa4038](https://github.com/edm-su/api/commit/cfa403880971f2e8be57e9b89a1eaddd7e165fe0)) - dependabot[bot]
- **(deps)** bump authzed from 0.11.0 to 0.14.0 (#533) - ([144eff5](https://github.com/edm-su/api/commit/144eff52a21cd39246ce402759ac4db35f5e24f4)) - dependabot[bot]
- **(deps)** bump mypy from 1.7.1 to 1.9.0 (#529) - ([e4c3cf1](https://github.com/edm-su/api/commit/e4c3cf18c9093c35ce831c50928895e617301aad)) - dependabot[bot]
- **(deps)** bump ruff from 0.2.2 to 0.3.3 (#532) - ([b9ea398](https://github.com/edm-su/api/commit/b9ea398e9006c82bff2cfae2bcf61dea677c9b50)) - dependabot[bot]
- **(deps)** bump sqlalchemy from 2.0.25 to 2.0.28 (#527) - ([6372c81](https://github.com/edm-su/api/commit/6372c818b17f15b41bb1f540b11b9888779946ff)) - dependabot[bot]
- **(deps)** bump fastapi from 0.109.2 to 0.110.0 (#523) - ([d89be67](https://github.com/edm-su/api/commit/d89be67e755af2710987a35a17d5c6161ad81cf3)) - dependabot[bot]
- **(deps)** bump typing-extensions from 4.8.0 to 4.10.0 (#524) - ([49b68bd](https://github.com/edm-su/api/commit/49b68bddffd90af5f9f2712ade29e4a283aaeae0)) - dependabot[bot]
- **(deps)** bump orjson from 3.9.9 to 3.9.15 (#525) - ([7860c19](https://github.com/edm-su/api/commit/7860c197384982564147a24924f960d2112a2e67)) - dependabot[bot]
- **(deps)** bump ruff from 0.2.1 to 0.2.2 (#521) - ([40e8cb3](https://github.com/edm-su/api/commit/40e8cb323dfe0b1ee0d7f704b99716069939113c)) - dependabot[bot]
- **(deps)** bump pre-commit from 3.5.0 to 3.6.2 (#519) - ([ada0c1a](https://github.com/edm-su/api/commit/ada0c1a6e7e945ef601bad063f14f1031398021f)) - dependabot[bot]
- **(deps)** bump ruff from 0.1.14 to 0.2.1 (#510) - ([77499c5](https://github.com/edm-su/api/commit/77499c576354ac34a8039b24aba110ae298c3b4d)) - dependabot[bot]
- **(deps)** bump fastapi from 0.109.0 to 0.109.2 (#509) - ([b381a51](https://github.com/edm-su/api/commit/b381a514013875cc358e08cc679131e1c118115b)) - dependabot[bot]
- **(deps)** bump aiohttp from 3.9.1 to 3.9.3 (#504) - ([6406202](https://github.com/edm-su/api/commit/6406202b9c3ec38de8fef7e6f455898604142f85)) - dependabot[bot]
- **(deps)** bump ruff from 0.1.13 to 0.1.14 (#498) - ([22b0871](https://github.com/edm-su/api/commit/22b0871b9f8ae65dd90483659f7be60b0a8da92f)) - dependabot[bot]
- **(deps)** bump aioboto3 from 12.0.0 to 12.2.0 (#497) - ([549d720](https://github.com/edm-su/api/commit/549d7201f0b562325d384f2857e67b876524c7d2)) - dependabot[bot]
- **(deps)** bump fastapi from 0.103.2 to 0.109.0 (#495) - ([e091402](https://github.com/edm-su/api/commit/e09140205a60162776d6ad7630933153821a7665)) - dependabot[bot]
- **(deps)** bump ruff from 0.1.7 to 0.1.13 (#496) - ([e415500](https://github.com/edm-su/api/commit/e41550071e296299f9fe4407267d9ea2fb62a4d8)) - dependabot[bot]
- **(deps)** bump pillow from 10.0.1 to 10.2.0 (#490) - ([0aff31d](https://github.com/edm-su/api/commit/0aff31dfcdb262a4c001245aaa093e113102100f)) - dependabot[bot]
- **(deps)** bump types-aiofiles from 23.2.0.0 to 23.2.0.20240106 (#491) - ([94272f1](https://github.com/edm-su/api/commit/94272f1e23bc85d06519118c82f034d91224bdda)) - dependabot[bot]
- **(deps)** bump sqlalchemy from 2.0.23 to 2.0.25 (#489) - ([6f82595](https://github.com/edm-su/api/commit/6f825959235490dd3f21df57ccb96770bb7b93ed)) - dependabot[bot]
- **(deps)** bump alembic from 1.13.0 to 1.13.1 (#481) - ([71d50e3](https://github.com/edm-su/api/commit/71d50e39ee6485378c61977734fb95918446790d)) - dependabot[bot]
- **(deps)** bump alembic from 1.12.1 to 1.13.0 (#470) - ([b81b892](https://github.com/edm-su/api/commit/b81b8926a5d42fff65ba1c6131ed4acd1ca5adf0)) - dependabot[bot]
- **(deps)** bump ruff from 0.1.6 to 0.1.7 (#472) - ([83a442e](https://github.com/edm-su/api/commit/83a442ecc7cbb63fde286e8255f048d9e5a558f8)) - dependabot[bot]
- **(deps)** bump mypy from 1.6.0 to 1.7.1 (#463) - ([f35d440](https://github.com/edm-su/api/commit/f35d4403084c56cf9e8a30f7c303a97be69ad486)) - dependabot[bot]
- **(deps)** bump aiohttp from 3.9.0b0 to 3.9.1 (#464) - ([5b05fcc](https://github.com/edm-su/api/commit/5b05fcc1d901a384b749009af0ec58f67ac7202e)) - dependabot[bot]
- **(deps)** bump pytest-mock from 3.11.1 to 3.12.0 (#465) - ([276bc7b](https://github.com/edm-su/api/commit/276bc7ba80b45ca641b61ec000c0a97ebdecfb6f)) - dependabot[bot]
#### Continuous Integration
- **(actions)** bump codecov/codecov-action from 3 to 4 (#506) - ([3ecd0e2](https://github.com/edm-su/api/commit/3ecd0e2013beaad2ca13f3294108f6a0747aca04)) - dependabot[bot]
- **(actions)** bump actions/setup-python from 4.6.1 to 5.0.0 (#474) - ([aef6888](https://github.com/edm-su/api/commit/aef68888a83636b027bdf2b204cae31c403c1412)) - dependabot[bot]
- **(actions)** bump google-github-actions/release-please-action (#467) - ([c8e7fde](https://github.com/edm-su/api/commit/c8e7fde8a96ad8046d98575463007fc75013e220)) - dependabot[bot]
- added paths rule (#566) - ([c764e67](https://github.com/edm-su/api/commit/c764e676eca53c17792c6a070bcbdefab64efee3)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 3.3.1 (#468) - ([395eb5e](https://github.com/edm-su/api/commit/395eb5ed7d6bc96652ca4876f97638023f03650d)) - Egor Gluhih
#### Tests
- fixed blocking calls (#511) - ([fb5a9b7](https://github.com/edm-su/api/commit/fb5a9b7445bb564e2783d0544818108621288bbe)) - Egor Gluhih

- - -

## [v3.3.0](https://github.com/edm-su/api/compare/v3.2.1..v3.3.0) - 2024-08-19
#### Bug Fixes
- **(deps)** bump pytest-httpx from 0.26.0 to 0.27.0 (#459) - ([3c97d41](https://github.com/edm-su/api/commit/3c97d413b005d3180cdfb5e0f06a35520fe8ae4d)) - dependabot[bot]
- **(deps)** bump asyncpg from 0.28.0 to 0.29.0 (#458) - ([a405a9e](https://github.com/edm-su/api/commit/a405a9e726781551e0cd3af375846339051f9869)) - dependabot[bot]
- **(deps)** bump sqlalchemy from 2.0.22 to 2.0.23 (#457) - ([421581f](https://github.com/edm-su/api/commit/421581f92dca77a98e721c85325bfb5342ce0eb0)) - dependabot[bot]
- **(deps)** bump aioboto3 from 11.3.1 to 12.0.0 (#460) - ([1d33280](https://github.com/edm-su/api/commit/1d3328008cd6e992d055de9cfb92f35ef03039c7)) - dependabot[bot]
- **(deps)** bump ruff from 0.0.292 to 0.1.6 (#454) - ([41ed402](https://github.com/edm-su/api/commit/41ed4021b0c101dccc75be77f080751ac9fe2994)) - dependabot[bot]
- **(deps)** bump alembic from 1.12.0 to 1.12.1 (#449) - ([dfdfc31](https://github.com/edm-su/api/commit/dfdfc317d8d74393a9a5a5c963a2a147b509d58e)) - dependabot[bot]
- **(deps)** bump urllib3 from 1.26.17 to 1.26.18 (#443) - ([857e78a](https://github.com/edm-su/api/commit/857e78ac5d58ba04293ddf71b52ce9d6122f1853)) - dependabot[bot]
- **(deps)** bump meilisearch-python-async from 1.6.2 to 1.8.0 (#420) - ([a328d79](https://github.com/edm-su/api/commit/a328d796c0254ee4885b052d016e7b77cb603c51)) - dependabot[bot]
- **(deps)** bump greenlet from 2.0.2 to 3.0.0 (#429) - ([18bfca9](https://github.com/edm-su/api/commit/18bfca907555e2816761a949ee7338ee961de6c2)) - dependabot[bot]
- **(deps)** bump ruff from 0.0.290 to 0.0.292 (#430) - ([2d7ded1](https://github.com/edm-su/api/commit/2d7ded1f7bb5e92047dd49a61cfa9044434da6dd)) - dependabot[bot]
#### Features
- add python 3.12 support (#431) - ([7f70403](https://github.com/edm-su/api/commit/7f704039be7c973d375a7742892fbdbedb156f86)) - Egor Gluhih
- change videos uniqueness logics (#432) - ([61d54a5](https://github.com/edm-su/api/commit/61d54a5eb869d5922e8fbdc6f8183d3e414ed6de)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 3.3.0 (#426) - ([85cb9b2](https://github.com/edm-su/api/commit/85cb9b2e63080f9193952edf5e7a4bbf8341add1)) - Egor Gluhih
#### Revert
- "fix(ci): change entrypoint to cmd (#423)" (#425) - ([a35d561](https://github.com/edm-su/api/commit/a35d561e240d70ec076cedb5368583245b91a56c)) - Egor Gluhih
#### Style
- update ruff rules (#456) - ([e0b1412](https://github.com/edm-su/api/commit/e0b1412241692ce2f79f51193e4054a4fcdf291b)) - Egor Gluhih
- replace black to ruff formatter (#455) - ([19e7853](https://github.com/edm-su/api/commit/19e78537354e190511ef365e63c60f5ca864de35)) - Egor Gluhih

- - -

## [v3.2.1](https://github.com/edm-su/api/compare/v3.2.0..v3.2.1) - 2024-08-19
#### Bug Fixes
- **(ci)** change entrypoint to cmd (#423) - ([f46cc78](https://github.com/edm-su/api/commit/f46cc78cbb3aaf6b204b7c15fc5716d0e3a10a02)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 3.2.1 (#424) - ([11351c8](https://github.com/edm-su/api/commit/11351c8ef0d60e9ab60acc9f762b9e919b94481a)) - Egor Gluhih

- - -

## [v3.2.0](https://github.com/edm-su/api/compare/v3.1.0..v3.2.0) - 2024-08-19
#### Bug Fixes
- **(deps)** bump fastapi from 0.101.1 to 0.103.2 (#421) - ([f231c33](https://github.com/edm-su/api/commit/f231c334c2145f8a382794fab964cc43c0f74561)) - dependabot[bot]
- **(deps)** bump sqlalchemy from 2.0.20 to 2.0.21 (#415) - ([bfdc706](https://github.com/edm-su/api/commit/bfdc70698e07ad432f6c7a24f97b66aac00b3f69)) - dependabot[bot]
- **(deps)** bump black from 23.7.0 to 23.9.1 (#411) - ([4a0716a](https://github.com/edm-su/api/commit/4a0716af28c46dbbede7582a4c8b245945e93833)) - dependabot[bot]
- **(deps)** bump pytest-httpx from 0.23.1 to 0.26.0 (#417) - ([74bca42](https://github.com/edm-su/api/commit/74bca429111051b79fd15eab7bf1efeceb93878e)) - dependabot[bot]
- **(deps)** bump typing-extensions from 4.7.1 to 4.8.0 (#416) - ([0254559](https://github.com/edm-su/api/commit/02545596f8624d7ef740d946d2be0611a16ccc2c)) - dependabot[bot]
- **(deps)** bump ruff from 0.0.287 to 0.0.290 (#412) - ([47e3e3a](https://github.com/edm-su/api/commit/47e3e3adbac690ea8e31e9c8a3a18f2334f4d836)) - dependabot[bot]
#### Continuous Integration
- **(actions)** bump docker/build-push-action from 4 to 5 (#409) - ([77609fd](https://github.com/edm-su/api/commit/77609fd72436b3a1891112cdaabb251d8c95d44a)) - dependabot[bot]
- **(actions)** bump docker/metadata-action from 4 to 5 (#406) - ([65e7e6e](https://github.com/edm-su/api/commit/65e7e6ec079e7b4a4e0c43f3762b36930c5a3da6)) - dependabot[bot]
- **(actions)** bump actions/checkout from 3 to 4 (#396) - ([3efbd0e](https://github.com/edm-su/api/commit/3efbd0e57cc863ba2d2f2f41023696a0a9901102)) - dependabot[bot]
- **(actions)** bump docker/login-action from 2 to 3 (#407) - ([104a750](https://github.com/edm-su/api/commit/104a75071267847e1d8e7db2805437c60fe2435b)) - dependabot[bot]
- **(actions)** bump docker/setup-buildx-action from 2 to 3 (#405) - ([54aca96](https://github.com/edm-su/api/commit/54aca962464109bd6d1bf7a17070eb5002c3d688)) - dependabot[bot]
- **(actions)** bump docker/setup-qemu-action from 2 to 3 (#408) - ([f0b7e0d](https://github.com/edm-su/api/commit/f0b7e0d2e354b623c4b9b863ae77f15e5e434642)) - dependabot[bot]
- added just build system (#414) - ([62590d8](https://github.com/edm-su/api/commit/62590d8693b12f92cd881ce00345e71ead0a03ef)) - Egor Gluhih
#### Features
- changed spicedb resources id to slug (#422) - ([f95a549](https://github.com/edm-su/api/commit/f95a549fc6f32c60668bff8bb35fa5e7a3099242)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 3.2.0 (#413) - ([c7357b1](https://github.com/edm-su/api/commit/c7357b104983ff2a880664e7247e723d7aeddb8e)) - Egor Gluhih

- - -

## [v3.1.0](https://github.com/edm-su/api/compare/v3.0.0..v3.1.0) - 2024-08-19
#### Bug Fixes
- **(deps)** bump ruff from 0.0.285 to 0.0.287 (#392) - ([a850e22](https://github.com/edm-su/api/commit/a850e229be98a1dfcd478484e9c4d8f53431a51b)) - dependabot[bot]
#### Features
- add encryption support for spicedb connection (#394) - ([d2d2197](https://github.com/edm-su/api/commit/d2d2197786957769bb52b3ca2db52d7d6af7df6f)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 3.1.0 (#395) - ([be92573](https://github.com/edm-su/api/commit/be92573f77028eeb2b84b8e0bb95e68a50c630a8)) - Egor Gluhih

- - -

## [v3.0.0](https://github.com/edm-su/api/compare/v2.6.0..v3.0.0) - 2024-08-19
#### Bug Fixes
- **(deps)** bump ruff from 0.0.284 to 0.0.285 (#381) - ([c6af3de](https://github.com/edm-su/api/commit/c6af3de5eefaf2324bf53c959644afa952ccb5c7)) - dependabot[bot]
- **(deps)** bump sqlalchemy from 2.0.18 to 2.0.20 (#377) - ([7e14b65](https://github.com/edm-su/api/commit/7e14b65e0917a00e68a43710bdd73ed45826ab74)) - dependabot[bot]
- **(deps)** bump aioboto3 from 11.2.0 to 11.3.0 (#380) - ([7bf2ee3](https://github.com/edm-su/api/commit/7bf2ee3ef64d31f8e3a8338e6a8e51a3e19202eb)) - dependabot[bot]
- **(deps)** bump mypy from 1.4.1 to 1.5.1 (#379) - ([e9f6939](https://github.com/edm-su/api/commit/e9f69391f85657aaa7435cbbc4a0f77f8a3da41e)) - dependabot[bot]
- **(deps)** bump fastapi from 0.101.0 to 0.101.1 (#376) - ([67f46c1](https://github.com/edm-su/api/commit/67f46c1b4bca910e659a29974a3e80a0de455c27)) - dependabot[bot]
- **(deps)** bump meilisearch-python-async from 1.6.1 to 1.6.2 (#375) - ([2b4258e](https://github.com/edm-su/api/commit/2b4258e54cc4fa7f23573f3d66fc5233b2333f52)) - dependabot[bot]
- **(deps)** bump meilisearch-python-async from 1.5.0 to 1.6.1 (#372) - ([3dbdf4f](https://github.com/edm-su/api/commit/3dbdf4fee76f71470144c7c0ca136d585a048aed)) - dependabot[bot]
- **(deps)** bump ruff from 0.0.282 to 0.0.284 (#371) - ([56d9251](https://github.com/edm-su/api/commit/56d92510f7cf6513e3e81ab75f8b3a0260a5da9f)) - dependabot[bot]
- **(deps)** bump alembic from 1.11.1 to 1.11.2 (#366) - ([0526211](https://github.com/edm-su/api/commit/052621175fba685d3f13d9a38e1b24279cfe0736)) - dependabot[bot]
- **(deps)** bump faker from 19.2.0 to 19.3.0 (#368) - ([6f53be8](https://github.com/edm-su/api/commit/6f53be865232b715101355d4f5c6e444ba39241a)) - dependabot[bot]
- **(deps)** bump fastapi from 0.100.1 to 0.101.0 (#367) - ([c414192](https://github.com/edm-su/api/commit/c414192ece2478b96b11fdda4a7a263014574599)) - dependabot[bot]
#### Continuous Integration
- fix mypy error (#385) - ([a942f03](https://github.com/edm-su/api/commit/a942f0316d158dd93bd5eb4f3b0871ae1c3645f8)) - Egor Gluhih
#### Features
- transfer authorization to the controller layer (#384) - ([659e5f6](https://github.com/edm-su/api/commit/659e5f63a7ea52944b351f5bf226fb87e7f1dea1)) - Egor Gluhih
- scopes mechanism added (#365) - ([2d1bbe1](https://github.com/edm-su/api/commit/2d1bbe1b352dbc35ceb3535e29b91e8861d15de7)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 3.0.0 (#373) - ([739985c](https://github.com/edm-su/api/commit/739985c37ed2f87a26edbebda1ec07440e8b5385)) - Egor Gluhih
- release 3.0.0 - ([f5caff9](https://github.com/edm-su/api/commit/f5caff9605bbe019edd6fa7ce55b20d3ae89e457)) - Egor Gluhih
#### Refactoring
- removed unused hashed_password fields (#363) - ([c9d79f5](https://github.com/edm-su/api/commit/c9d79f5f0932654b89cd4b17090f3a60592c7956)) - Egor Gluhih

- - -

## [v2.6.0](https://github.com/edm-su/api/compare/v2.5.0..v2.6.0) - 2024-08-19
#### Bug Fixes
- **(deps)** bump pytest-httpx from 0.23.0 to 0.23.1 (#360) - ([e2b7b55](https://github.com/edm-su/api/commit/e2b7b55fa1c6970c7e6638b59ef57e7cf66ba625)) - dependabot[bot]
- **(deps)** bump types-python-slugify from 8.0.0.2 to 8.0.0.3 (#348) - ([1d84344](https://github.com/edm-su/api/commit/1d843443f03d32a9a343ed3afbdf4bae2f70b8f3)) - dependabot[bot]
- **(deps)** bump pytest-httpx from 0.22.0 to 0.23.0 (#356) - ([e77a4ce](https://github.com/edm-su/api/commit/e77a4ce2afbbf80935b5f30f5658bc5bb61a3386)) - dependabot[bot]
- **(deps)** bump meilisearch-python-async from 1.4.4 to 1.5.0 (#355) - ([a42b62c](https://github.com/edm-su/api/commit/a42b62c0cd2b0f60f51f5168ebc22a5b924ea8f1)) - dependabot[bot]
- **(deps)** bump faker from 15.3.4 to 19.2.0 (#349) - ([6ef46f3](https://github.com/edm-su/api/commit/6ef46f3f31fee76ac819a96ff32ed4c01df488a4)) - dependabot[bot]
- **(deps)** bump ruff from 0.0.280 to 0.0.282 (#357) - ([21424a9](https://github.com/edm-su/api/commit/21424a9ccbdb629f4fc60165009e9a84e2cb761f)) - dependabot[bot]
- default api token expiration time (#361) - ([06005c8](https://github.com/edm-su/api/commit/06005c8620665b36c6bb12c9e0f9180d5abdaba7)) - Egor Gluhih
#### Features
- added authorization at password change (#362) - ([0e43c8d](https://github.com/edm-su/api/commit/0e43c8d1203e2e27efe6986f66b6c4b367408cf8)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 2.6.0 (#359) - ([9409472](https://github.com/edm-su/api/commit/940947269d662ddee8614c547ee2a6bc251a42f6)) - Egor Gluhih

- - -

## [v2.5.0](https://github.com/edm-su/api/compare/v2.4.5..v2.5.0) - 2024-08-19
#### Bug Fixes
- **(deps)** bump fastapi from 0.100.0 to 0.100.1 (#352) - ([237193a](https://github.com/edm-su/api/commit/237193a281e5f107b0d8cc2f89c50912e0cfd81e)) - dependabot[bot]
- **(deps)** bump pydantic from 2.0.2 to 2.1.1 (#353) - ([397e0a5](https://github.com/edm-su/api/commit/397e0a5a6c01980e31f6670a256447eb7a1a7bce)) - Egor Gluhih
- **(deps)** bump certifi from 2022.12.7 to 2023.7.22 (#351) - ([b7dea76](https://github.com/edm-su/api/commit/b7dea7672d1332013668fe9c50cd741d95d40d33)) - dependabot[bot]
- **(deps)** bump ruff from 0.0.278 to 0.0.280 (#350) - ([1b36684](https://github.com/edm-su/api/commit/1b366843354cf6db1c143c5dc460b43af5450bfb)) - dependabot[bot]
- **(deps)** bump pytest-asyncio from 0.21.0 to 0.21.1 (#339) - ([5a1484e](https://github.com/edm-su/api/commit/5a1484e12576afd982418b106decf05a45d32729)) - dependabot[bot]
- **(deps)** bump ruff from 0.0.277 to 0.0.278 (#340) - ([25a2efb](https://github.com/edm-su/api/commit/25a2efbc1ab3d4047ac60df7fd60b6968a240ba3)) - dependabot[bot]
- **(deps)** bump black from 23.3.0 to 23.7.0 (#334) - ([3365c8b](https://github.com/edm-su/api/commit/3365c8ba6b9b155ad7f9bf7f52e228c35c7ded6a)) - dependabot[bot]
#### Features
- divide complete password recovery and change password (#338) - ([d0dc565](https://github.com/edm-su/api/commit/d0dc56535c97f4c8b6333fd7a6b92b54c5e41ee7)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 2.5.0 (#335) - ([192c267](https://github.com/edm-su/api/commit/192c26737d0799a86328ba06ccd183cff7dbb999)) - Egor Gluhih

- - -

## [v2.4.5](https://github.com/edm-su/api/compare/v2.4.4..v2.4.5) - 2024-08-19
#### Bug Fixes
- **(deps)** bump fastapi from 0.99.1 to 0.100.0 (#333) - ([6e54d47](https://github.com/edm-su/api/commit/6e54d47ffa3459440bf425dffb326d9a720d90c4)) - dependabot[bot]
- **(deps)** bump meilisearch-python-async from 1.2.2 to 1.4.4 (#323) - ([9ecf350](https://github.com/edm-su/api/commit/9ecf3506c216111baf2a184058fe005b9b40da3a)) - dependabot[bot]
- **(deps)** bump pillow from 9.5.0 to 10.0.0 (#330) - ([0b32c6f](https://github.com/edm-su/api/commit/0b32c6f51e511aa57087a2d8d67705d86a8760f1)) - dependabot[bot]
- **(deps)** bump ruff from 0.0.275 to 0.0.277 (#332) - ([2b9049f](https://github.com/edm-su/api/commit/2b9049f5d416433bfcdb7ea960d68e96cf4f3985)) - dependabot[bot]
- **(deps)** bump fastapi from 0.98.0 to 0.99.1 (#331) - ([97152b8](https://github.com/edm-su/api/commit/97152b89382cace04612758e718aaba7163a7456)) - dependabot[bot]
- **(deps)** bump pytest from 7.2.2 to 7.4.0 (#319) - ([56f0b34](https://github.com/edm-su/api/commit/56f0b3444ddc531fa6007611c56bc52d9eb73c9e)) - dependabot[bot]
- **(deps)** bump pytest-mock from 3.10.0 to 3.11.1 (#292) - ([208dff4](https://github.com/edm-su/api/commit/208dff4a41d358412cc39ea84e46d97d9f093297)) - dependabot[bot]
- **(deps)** bump typing-extensions from 4.6.3 to 4.7.1 (#322) - ([042f5bb](https://github.com/edm-su/api/commit/042f5bb28b1d5bf514d846549a56e0a3162a4d74)) - dependabot[bot]
- **(deps)** bump sqlalchemy from 2.0.16 to 2.0.18 (#327) - ([d0b0416](https://github.com/edm-su/api/commit/d0b04169cd679c2b507a3296c856d342f8e27a53)) - dependabot[bot]
#### Miscellaneous Chores
- **(master)** release 2.4.5 (#328) - ([ff32430](https://github.com/edm-su/api/commit/ff3243058cde81d208647d6a40d116d78b72bbc7)) - Egor Gluhih

- - -

## [v2.4.4](https://github.com/edm-su/api/compare/v2.4.3..v2.4.4) - 2024-08-19
#### Bug Fixes
- published_at format (#325) - ([524df3f](https://github.com/edm-su/api/commit/524df3f62111abd8ca66fd15ce09515616015b9c)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 2.4.4 (#326) - ([2bcccd9](https://github.com/edm-su/api/commit/2bcccd9b3feca03bad7703befe5857c52cf5b942)) - Egor Gluhih

- - -

## [v2.4.3](https://github.com/edm-su/api/compare/v2.4.2..v2.4.3) - 2024-08-19
#### Bug Fixes
- **(deps)** bump fastapi from 0.97.0 to 0.98.0 (#314) - ([e3044a4](https://github.com/edm-su/api/commit/e3044a426c5744734c6540b05e47a720fd8ea4cf)) - dependabot[bot]
- **(deps)** bump mypy from 1.3.0 to 1.4.1 (#315) - ([d409b78](https://github.com/edm-su/api/commit/d409b786c75026e13e7dd54f12dc6ea5bc430bd5)) - dependabot[bot]
- **(deps)** bump ruff from 0.0.272 to 0.0.275 (#313) - ([ddc9138](https://github.com/edm-su/api/commit/ddc9138217c560f998093976a55562e3ba2027c0)) - dependabot[bot]
- not found post error (#320) - ([8134af3](https://github.com/edm-su/api/commit/8134af3d20d3cdedc4400fc3c2e3eec55d929a2a)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 2.4.3 (#317) - ([30c0c5c](https://github.com/edm-su/api/commit/30c0c5c40605320702f915fad3cf5d79db6e8774)) - Egor Gluhih

- - -

## [v2.4.2](https://github.com/edm-su/api/compare/v2.4.1..v2.4.2) - 2024-08-19
#### Bug Fixes
- conflict on create video (#311) - ([c70702b](https://github.com/edm-su/api/commit/c70702badb4e596599f86f0619930109658c8eef)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 2.4.2 (#312) - ([5be89c4](https://github.com/edm-su/api/commit/5be89c425265eba7136215266b5a787f8ba5e08c)) - Egor Gluhih

- - -

## [v2.4.1](https://github.com/edm-su/api/compare/v2.4.0..v2.4.1) - 2024-08-19
#### Bug Fixes
- timezone error (#306) - ([0b541dc](https://github.com/edm-su/api/commit/0b541dc888ae833d0727a49c65e933b53a428c78)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 2.4.1 (#307) - ([938755c](https://github.com/edm-su/api/commit/938755c0c0278f867a78e93e50f0e4093e91bc33)) - Egor Gluhih

- - -

## [v2.4.0](https://github.com/edm-su/api/compare/v2.3.1..v2.4.0) - 2024-08-19
#### Features
- added update tokens (#304) - ([db6ea5c](https://github.com/edm-su/api/commit/db6ea5cf36758b3853465e26a050a4fe237bf052)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 2.4.0 (#305) - ([4270411](https://github.com/edm-su/api/commit/42704114829ee769e97a7ae8ffb672cb7b685df3)) - Egor Gluhih

- - -

## [v2.3.1](https://github.com/edm-su/api/compare/v2.3.0..v2.3.1) - 2024-08-19
#### Bug Fixes
- uvicorn run (#302) - ([0021614](https://github.com/edm-su/api/commit/0021614fee4c3d1339f65ba375582e86d18ec943)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 2.3.1 (#303) - ([edf3724](https://github.com/edm-su/api/commit/edf37241d8b6a5e203c81fd5f8dbe6ece737d204)) - Egor Gluhih

- - -

## [v2.3.0](https://github.com/edm-su/api/compare/v2.2.3..v2.3.0) - 2024-08-19
#### Documentation
- update environment variables description (#299) - ([5829338](https://github.com/edm-su/api/commit/58293382a88956346d85de1ea112eed21d01af1d)) - Egor Gluhih
#### Features
- added host and port config (#301) - ([b6219e6](https://github.com/edm-su/api/commit/b6219e641b96ff60b30037c0a32ccc29492f3d4b)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 2.3.0 (#300) - ([f989df3](https://github.com/edm-su/api/commit/f989df31faa6eed08a501d4640db117f3a943100)) - Egor Gluhih

- - -

## [v2.2.3](https://github.com/edm-su/api/compare/v2.2.2..v2.2.3) - 2024-08-19
#### Bug Fixes
- default log level (#297) - ([d45b3d9](https://github.com/edm-su/api/commit/d45b3d999cf2ba15549e1854b0c728eef70a372e)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 2.2.3 (#298) - ([dbd7534](https://github.com/edm-su/api/commit/dbd753471e78528e782a583060acb0bbbc76e8de)) - Egor Gluhih

- - -

## [v2.2.2](https://github.com/edm-su/api/compare/v2.2.1..v2.2.2) - 2024-08-19
#### Bug Fixes
- entrypoint (#295) - ([7865086](https://github.com/edm-su/api/commit/78650867a6c23d7c803ad032d07b02a8e60534fc)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 2.2.2 (#296) - ([9893e07](https://github.com/edm-su/api/commit/9893e07e790bbd86902f80d93490f0114d252bdd)) - Egor Gluhih

- - -

## [v2.2.1](https://github.com/edm-su/api/compare/v2.2.0..v2.2.1) - 2024-08-19
#### Bug Fixes
- migrations (#293) - ([8d3c40f](https://github.com/edm-su/api/commit/8d3c40fd05a51169a5e1d8983a5fa47752f93ecf)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 2.2.1 (#294) - ([2e6f1d2](https://github.com/edm-su/api/commit/2e6f1d2fb8b5503c85d014f1811f6b77d3911589)) - Egor Gluhih

- - -

## [v2.2.0](https://github.com/edm-su/api/compare/v2.1.2..v2.2.0) - 2024-08-19
#### Bug Fixes
- **(deps)** bump sqlalchemy from 2.0.15 to 2.0.16 (#288) - ([a2fba6e](https://github.com/edm-su/api/commit/a2fba6e70ea301e4134a83e625355ac2cd075576)) - dependabot[bot]
- **(deps)** bump ruff from 0.0.271 to 0.0.272 (#286) - ([d318b0d](https://github.com/edm-su/api/commit/d318b0dc053ce90d2aafa39a96704838a72860c8)) - dependabot[bot]
- **(deps)** bump fastapi from 0.96.0 to 0.97.0 (#289) - ([01550f6](https://github.com/edm-su/api/commit/01550f67580f2bf698e2dd11b0eddd3e6c9d05ed)) - dependabot[bot]
#### Features
- remove sending email (#291) - ([a050f38](https://github.com/edm-su/api/commit/a050f385f5b13376eaa450e5bac9671284ff32ed)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 2.2.0 (#290) - ([870158e](https://github.com/edm-su/api/commit/870158e30c51c91be150310f6c652288f7371547)) - Egor Gluhih

- - -

## [v2.1.2](https://github.com/edm-su/api/compare/v2.1.1..v2.1.2) - 2024-08-19
#### Bug Fixes
- **(deps)** bump typing-extensions from 4.6.0 to 4.6.3 (#280) - ([dc89797](https://github.com/edm-su/api/commit/dc8979729256190514f19eb572eeee7bd78c8bda)) - dependabot[bot]
- **(deps)** bump fastapi from 0.95.2 to 0.96.0 (#281) - ([fa4ca4d](https://github.com/edm-su/api/commit/fa4ca4d7389d52979a986e7279e2a594366b870e)) - dependabot[bot]
- **(deps)** bump ruff from 0.0.270 to 0.0.271 (#284) - ([7af9a9f](https://github.com/edm-su/api/commit/7af9a9f44a98876eeb455d42cedb6a0868ae6a49)) - dependabot[bot]
- get videos order (#282) - ([a0b9626](https://github.com/edm-su/api/commit/a0b96264ac05f578f6d96de3558dd518024c4402)) - Egor Gluhih
- changed password hashing algorithm (#278) - ([f0cd9ac](https://github.com/edm-su/api/commit/f0cd9ac6ded078749042569982300c2584da2b16)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 2.1.2 (#279) - ([97ce027](https://github.com/edm-su/api/commit/97ce02717eaa716294e06ea7655044865c2471ad)) - Egor Gluhih

- - -

## [v2.1.1](https://github.com/edm-su/api/compare/v2.1.0..v2.1.1) - 2024-08-19
#### Bug Fixes
- **(deps)** bump ruff from 0.0.269 to 0.0.270 (#273) - ([4288613](https://github.com/edm-su/api/commit/428861357463583520e74b4badaa75ab36e74948)) - dependabot[bot]
- always returned "user already exists" (#276) - ([eb970f2](https://github.com/edm-su/api/commit/eb970f24a09f98cc5b5e6224d87f54b48ba3f110)) - Egor Gluhih
#### Continuous Integration
- **(actions)** bump actions/setup-python from 4.5.0 to 4.6.1 (#271) - ([dd4e09f](https://github.com/edm-su/api/commit/dd4e09f26155403757aef28d98a1103612bddcfa)) - dependabot[bot]
#### Miscellaneous Chores
- **(master)** release 2.1.1 (#274) - ([f969002](https://github.com/edm-su/api/commit/f969002de5b7c302252ac08e3705f093ce9870ed)) - Egor Gluhih

- - -

## [v2.1.0](https://github.com/edm-su/api/compare/b918a70984cbfc7413189027b8cec4cd9337def3..v2.1.0) - 2024-08-19
#### Bug Fixes
- **(deps)** bump mypy from 1.1.1 to 1.3.0 (#268) - ([04b6552](https://github.com/edm-su/api/commit/04b65528f3340d9bfd0638c87d785675cba87010)) - Egor Gluhih
- **(deps)** bump typing-extensions from 4.5.0 to 4.6.0 (#265) - ([e751971](https://github.com/edm-su/api/commit/e751971659791e31dfb72c1a7af275bbe877806e)) - dependabot[bot]
- **(deps)** bump sqlalchemy from 2.0.14 to 2.0.15 (#260) - ([6436e61](https://github.com/edm-su/api/commit/6436e61f3d7d8b842299f6aff6ef16869b00855b)) - dependabot[bot]
- **(deps)** bump pyjwt from 2.6.0 to 2.7.0 (#262) - ([30ca609](https://github.com/edm-su/api/commit/30ca6090d8296bc8dcf9a3a8b5ad8bc624b6155b)) - dependabot[bot]
- **(deps)** bump greenlet from 1.1.3.post0 to 2.0.2 (#261) - ([fa287cd](https://github.com/edm-su/api/commit/fa287cde20a4e5bfd5e889f7a9718a276f7be1d8)) - dependabot[bot]
- **(deps)** remove gunicorn (#253) - ([93ca0c7](https://github.com/edm-su/api/commit/93ca0c7654a5fcab79b14be14b6d72b15ee8cedb)) - Egor Gluhih
- **(deps)** bump sqlalchemy from 2.0.9 to 2.0.14 (#249) - ([4ddb07a](https://github.com/edm-su/api/commit/4ddb07a12eaabbeaf6249f1a8d3d2983ff7da66d)) - dependabot[bot]
- **(deps)** bump alembic from 1.10.2 to 1.11.1 (#241) - ([512d604](https://github.com/edm-su/api/commit/512d604ad8a26a822f52bb5faf6d76f979d0058b)) - dependabot[bot]
- **(deps)** bump fastapi from 0.94.1 to 0.95.2 (#240) - ([118a2c3](https://github.com/edm-su/api/commit/118a2c3be6feb5df644241b533e5a1f238d97deb)) - dependabot[bot]
- **(deps)** bump meilisearch-python-async from 1.1.0 to 1.2.2 (#246) - ([01d08b3](https://github.com/edm-su/api/commit/01d08b3f17295e739963dfaa7df273dbee60eaf3)) - dependabot[bot]
- The sign-in response no longer returns asterisks (#269) - ([8508259](https://github.com/edm-su/api/commit/8508259019387faa279ce77139701de37eac2716)) - Egor Gluhih
#### Build system
- **(python)** bump aioboto3 from 10.4.0 to 11.2.0 (#237) - ([b918a70](https://github.com/edm-su/api/commit/b918a70984cbfc7413189027b8cec4cd9337def3)) - dependabot[bot]
#### Continuous Integration
- **(actions)** remove github test environment (#254) - ([a84c8e6](https://github.com/edm-su/api/commit/a84c8e6eba5e10e1f523c8e0284ed28ab216a52e)) - Egor Gluhih
- **(dependabot)** change python prefixes (#245) - ([c717abc](https://github.com/edm-su/api/commit/c717abcf4bb0dd5b02fd29d48ced2d5c82b55ab0)) - Egor Gluhih
- change release-please token (#251) - ([959696d](https://github.com/edm-su/api/commit/959696d6c81074c45ecea8d6e208160fc13e0dd9)) - Egor Gluhih
#### Features
- migration to SqlAlchemy 2.0 ORM (#257) - ([7fd352f](https://github.com/edm-su/api/commit/7fd352f946b140a93319ac7ad90cf39e219efd1d)) - Egor Gluhih
- added SqlAlchemy 2.0 AsyncTransaction (#255) - ([e225e07](https://github.com/edm-su/api/commit/e225e07a1b02f28316ad70be3f015776f1fc75b1)) - Egor Gluhih
#### Miscellaneous Chores
- **(master)** release 2.1.0 (#247) - ([ffacdb8](https://github.com/edm-su/api/commit/ffacdb84da7a4b0fc9398502490844fe9b7b664b)) - github-actions[bot]
#### Style
- **(deps)** bump ruff from 0.0.262 to 0.0.269 (#259) - ([741aa06](https://github.com/edm-su/api/commit/741aa06fd25e075d0b4a9f952c2d5f9cc15906ee)) - dependabot[bot]
#### Tests
- fix faker pyint min value for id (#248) - ([0f97d48](https://github.com/edm-su/api/commit/0f97d4815273536213833bf10682f9e1c0802569)) - Egor Gluhih


