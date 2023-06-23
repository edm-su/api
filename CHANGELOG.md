# Changelog

## [2.4.2](https://github.com/edm-su/api/compare/v2.4.1...v2.4.2) (2023-06-23)


### Bug Fixes

* conflict on create video ([#311](https://github.com/edm-su/api/issues/311)) ([c70702b](https://github.com/edm-su/api/commit/c70702badb4e596599f86f0619930109658c8eef))

## [2.4.1](https://github.com/edm-su/api/compare/v2.4.0...v2.4.1) (2023-06-20)


### Bug Fixes

* timezone error ([#306](https://github.com/edm-su/api/issues/306)) ([0b541dc](https://github.com/edm-su/api/commit/0b541dc888ae833d0727a49c65e933b53a428c78))

## [2.4.0](https://github.com/edm-su/api/compare/v2.3.1...v2.4.0) (2023-06-16)


### Features

* added update tokens ([#304](https://github.com/edm-su/api/issues/304)) ([db6ea5c](https://github.com/edm-su/api/commit/db6ea5cf36758b3853465e26a050a4fe237bf052))

## [2.3.1](https://github.com/edm-su/api/compare/v2.3.0...v2.3.1) (2023-06-16)


### Bug Fixes

* uvicorn run ([#302](https://github.com/edm-su/api/issues/302)) ([0021614](https://github.com/edm-su/api/commit/0021614fee4c3d1339f65ba375582e86d18ec943))

## [2.3.0](https://github.com/edm-su/api/compare/v2.2.3...v2.3.0) (2023-06-16)


### Features

* added host and port config ([#301](https://github.com/edm-su/api/issues/301)) ([b6219e6](https://github.com/edm-su/api/commit/b6219e641b96ff60b30037c0a32ccc29492f3d4b))


### Documentation

* update environment variables description ([#299](https://github.com/edm-su/api/issues/299)) ([5829338](https://github.com/edm-su/api/commit/58293382a88956346d85de1ea112eed21d01af1d))

## [2.2.3](https://github.com/edm-su/api/compare/v2.2.2...v2.2.3) (2023-06-16)


### Bug Fixes

* default log level ([#297](https://github.com/edm-su/api/issues/297)) ([d45b3d9](https://github.com/edm-su/api/commit/d45b3d999cf2ba15549e1854b0c728eef70a372e))

## [2.2.2](https://github.com/edm-su/api/compare/v2.2.1...v2.2.2) (2023-06-16)


### Bug Fixes

* entrypoint ([#295](https://github.com/edm-su/api/issues/295)) ([7865086](https://github.com/edm-su/api/commit/78650867a6c23d7c803ad032d07b02a8e60534fc))

## [2.2.1](https://github.com/edm-su/api/compare/v2.2.0...v2.2.1) (2023-06-16)


### Bug Fixes

* migrations ([#293](https://github.com/edm-su/api/issues/293)) ([8d3c40f](https://github.com/edm-su/api/commit/8d3c40fd05a51169a5e1d8983a5fa47752f93ecf))

## [2.2.0](https://github.com/edm-su/api/compare/v2.1.2...v2.2.0) (2023-06-14)


### Features

* remove sending email ([#291](https://github.com/edm-su/api/issues/291)) ([a050f38](https://github.com/edm-su/api/commit/a050f385f5b13376eaa450e5bac9671284ff32ed))


### Bug Fixes

* **deps:** bump fastapi from 0.96.0 to 0.97.0 ([#289](https://github.com/edm-su/api/issues/289)) ([01550f6](https://github.com/edm-su/api/commit/01550f67580f2bf698e2dd11b0eddd3e6c9d05ed))
* **deps:** bump ruff from 0.0.271 to 0.0.272 ([#286](https://github.com/edm-su/api/issues/286)) ([d318b0d](https://github.com/edm-su/api/commit/d318b0dc053ce90d2aafa39a96704838a72860c8))
* **deps:** bump sqlalchemy from 2.0.15 to 2.0.16 ([#288](https://github.com/edm-su/api/issues/288)) ([a2fba6e](https://github.com/edm-su/api/commit/a2fba6e70ea301e4134a83e625355ac2cd075576))

## [2.1.2](https://github.com/edm-su/api/compare/v2.1.1...v2.1.2) (2023-06-07)


### Bug Fixes

* changed password hashing algorithm ([#278](https://github.com/edm-su/api/issues/278)) ([f0cd9ac](https://github.com/edm-su/api/commit/f0cd9ac6ded078749042569982300c2584da2b16)), closes [#277](https://github.com/edm-su/api/issues/277)
* **deps:** bump fastapi from 0.95.2 to 0.96.0 ([#281](https://github.com/edm-su/api/issues/281)) ([fa4ca4d](https://github.com/edm-su/api/commit/fa4ca4d7389d52979a986e7279e2a594366b870e))
* **deps:** bump ruff from 0.0.270 to 0.0.271 ([#284](https://github.com/edm-su/api/issues/284)) ([7af9a9f](https://github.com/edm-su/api/commit/7af9a9f44a98876eeb455d42cedb6a0868ae6a49))
* **deps:** bump typing-extensions from 4.6.0 to 4.6.3 ([#280](https://github.com/edm-su/api/issues/280)) ([dc89797](https://github.com/edm-su/api/commit/dc8979729256190514f19eb572eeee7bd78c8bda))
* get videos order ([#282](https://github.com/edm-su/api/issues/282)) ([a0b9626](https://github.com/edm-su/api/commit/a0b96264ac05f578f6d96de3558dd518024c4402))

## [2.1.1](https://github.com/edm-su/api/compare/v2.1.0...v2.1.1) (2023-05-26)


### Bug Fixes

* always returned "user already exists" ([#276](https://github.com/edm-su/api/issues/276)) ([eb970f2](https://github.com/edm-su/api/commit/eb970f24a09f98cc5b5e6224d87f54b48ba3f110))
* **deps:** bump ruff from 0.0.269 to 0.0.270 ([#273](https://github.com/edm-su/api/issues/273)) ([4288613](https://github.com/edm-su/api/commit/428861357463583520e74b4badaa75ab36e74948))

## [2.1.0](https://github.com/edm-su/api/compare/v2.0.0...v2.1.0) (2023-05-23)


### Features

* added SqlAlchemy 2.0 AsyncTransaction ([#255](https://github.com/edm-su/api/issues/255)) ([e225e07](https://github.com/edm-su/api/commit/e225e07a1b02f28316ad70be3f015776f1fc75b1))
* migration to SqlAlchemy 2.0 ORM ([#257](https://github.com/edm-su/api/issues/257)) ([7fd352f](https://github.com/edm-su/api/commit/7fd352f946b140a93319ac7ad90cf39e219efd1d))


### Bug Fixes

* **deps:** bump alembic from 1.10.2 to 1.11.1 ([#241](https://github.com/edm-su/api/issues/241)) ([512d604](https://github.com/edm-su/api/commit/512d604ad8a26a822f52bb5faf6d76f979d0058b))
* **deps:** bump fastapi from 0.94.1 to 0.95.2 ([#240](https://github.com/edm-su/api/issues/240)) ([118a2c3](https://github.com/edm-su/api/commit/118a2c3be6feb5df644241b533e5a1f238d97deb))
* **deps:** bump greenlet from 1.1.3.post0 to 2.0.2 ([#261](https://github.com/edm-su/api/issues/261)) ([fa287cd](https://github.com/edm-su/api/commit/fa287cde20a4e5bfd5e889f7a9718a276f7be1d8))
* **deps:** bump meilisearch-python-async from 1.1.0 to 1.2.2 ([#246](https://github.com/edm-su/api/issues/246)) ([01d08b3](https://github.com/edm-su/api/commit/01d08b3f17295e739963dfaa7df273dbee60eaf3))
* **deps:** bump mypy from 1.1.1 to 1.3.0 ([#268](https://github.com/edm-su/api/issues/268)) ([04b6552](https://github.com/edm-su/api/commit/04b65528f3340d9bfd0638c87d785675cba87010))
* **deps:** bump pyjwt from 2.6.0 to 2.7.0 ([#262](https://github.com/edm-su/api/issues/262)) ([30ca609](https://github.com/edm-su/api/commit/30ca6090d8296bc8dcf9a3a8b5ad8bc624b6155b))
* **deps:** bump sqlalchemy from 2.0.14 to 2.0.15 ([#260](https://github.com/edm-su/api/issues/260)) ([6436e61](https://github.com/edm-su/api/commit/6436e61f3d7d8b842299f6aff6ef16869b00855b))
* **deps:** bump sqlalchemy from 2.0.9 to 2.0.14 ([#249](https://github.com/edm-su/api/issues/249)) ([4ddb07a](https://github.com/edm-su/api/commit/4ddb07a12eaabbeaf6249f1a8d3d2983ff7da66d))
* **deps:** bump typing-extensions from 4.5.0 to 4.6.0 ([#265](https://github.com/edm-su/api/issues/265)) ([e751971](https://github.com/edm-su/api/commit/e751971659791e31dfb72c1a7af275bbe877806e))
* **deps:** remove gunicorn ([#253](https://github.com/edm-su/api/issues/253)) ([93ca0c7](https://github.com/edm-su/api/commit/93ca0c7654a5fcab79b14be14b6d72b15ee8cedb))
* The sign-in response no longer returns asterisks ([#269](https://github.com/edm-su/api/issues/269)) ([8508259](https://github.com/edm-su/api/commit/8508259019387faa279ce77139701de37eac2716)), closes [#264](https://github.com/edm-su/api/issues/264)

## [2.0.0](https://github.com/edm-su/api/compare/v1.5.1...v2.0.0) (2023-05-18)


### ⚠ BREAKING CHANGES

* rewritten using a clean architecture

### Code Refactoring

* rewritten using a clean architecture ([a21b8c1](https://github.com/edm-su/api/commit/a21b8c1fdde2caab406e408603ac1ca8daa666ba))

## [1.5.1](https://github.com/edm-su/api/compare/v1.5.0...v1.5.1) (2023-04-03)


### Bug Fixes

* changed the minimum version of meilisearch ([#219](https://github.com/edm-su/api/issues/219)) ([947468b](https://github.com/edm-su/api/commit/947468bbb22886d0355826c448fd9f92cd223fa7))

## [1.5.0](https://github.com/edm-su/api/compare/v1.4.5...v1.5.0) (2023-03-31)


### Features

* new release ([#209](https://github.com/edm-su/api/issues/209)) ([4218540](https://github.com/edm-su/api/commit/421854026cd21e8400747bb5ed4a205ff897f7e8))
