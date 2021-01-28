# Changelog

## [v2.15.0](https://github.com/solvebio/solvebio-python/tree/v2.15.0) (2021-01-08)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.14.1...v2.15.0)

**Closed issues:**

- Dataset/File query raises an error when it has been sliced and a stop param is set to float\('inf'\) [\#385](https://github.com/solvebio/solvebio-python/issues/385)

**Merged pull requests:**

- Handle parallel migrations [\#387](https://github.com/solvebio/solvebio-python/pull/387) ([davidhpark](https://github.com/davidhpark))
- Handle a query slicing when the potential number of returned records in the query is larger than the number of records left in the dataset/file [\#386](https://github.com/solvebio/solvebio-python/pull/386) ([nikolamaric](https://github.com/nikolamaric))
- Enable using filters, fields, exclude\_fields for a QueryFile object. [\#382](https://github.com/solvebio/solvebio-python/pull/382) ([nikolamaric](https://github.com/nikolamaric))

## [v2.14.1](https://github.com/solvebio/solvebio-python/tree/v2.14.1) (2020-12-04)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.14.0...v2.14.1)

**Closed issues:**

- Don't change data types to object in joins for list fields [\#380](https://github.com/solvebio/solvebio-python/issues/380)

**Merged pull requests:**

- Flatten lists of lists instead of using "object" data type in joins [\#379](https://github.com/solvebio/solvebio-python/pull/379) ([davecap](https://github.com/davecap))

## [v2.14.0](https://github.com/solvebio/solvebio-python/tree/v2.14.0) (2020-12-01)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.13.1...v2.14.0)

**Closed issues:**

- Test is creating a DatasetTemplate on every run [\#362](https://github.com/solvebio/solvebio-python/issues/362)

**Merged pull requests:**

- Use a different fake dataset ID [\#378](https://github.com/solvebio/solvebio-python/pull/378) ([davecap](https://github.com/davecap))
- Add support for archiving and restoring datasets [\#377](https://github.com/solvebio/solvebio-python/pull/377) ([jsh2134](https://github.com/jsh2134))
- Update mock [\#376](https://github.com/solvebio/solvebio-python/pull/376) ([jsh2134](https://github.com/jsh2134))
- Update Travis to Ubuntu 18.04 [\#375](https://github.com/solvebio/solvebio-python/pull/375) ([damnjanovictanja](https://github.com/damnjanovictanja))
- Update to newest HGNC [\#374](https://github.com/solvebio/solvebio-python/pull/374) ([damnjanovictanja](https://github.com/damnjanovictanja))

## [v2.13.1](https://github.com/solvebio/solvebio-python/tree/v2.13.1) (2020-10-14)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.13.0...v2.13.1)

**Merged pull requests:**

- Fix object serialize\(\) for missing metadata attribute [\#372](https://github.com/solvebio/solvebio-python/pull/372) ([davecap](https://github.com/davecap))

## [v2.13.0](https://github.com/solvebio/solvebio-python/tree/v2.13.0) (2020-10-14)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.12.0...v2.13.0)

**Implemented enhancements:**

- Add ability to query files and join datasets [\#363](https://github.com/solvebio/solvebio-python/pull/363) ([nikolamaric](https://github.com/nikolamaric))

**Fixed bugs:**

- Chaining join methods doesn't return an expected result [\#370](https://github.com/solvebio/solvebio-python/issues/370)
- Failure to upload folders of files containing chinese chars [\#365](https://github.com/solvebio/solvebio-python/issues/365)
- Modifying object attributes that are dictionaries may not save updates  [\#276](https://github.com/solvebio/solvebio-python/issues/276)

**Closed issues:**

- Metadata as class\<str\> after saving empty metadata [\#324](https://github.com/solvebio/solvebio-python/issues/324)

**Merged pull requests:**

- add version and name to recipes script [\#368](https://github.com/solvebio/solvebio-python/pull/368) ([jsh2134](https://github.com/jsh2134))
- Sync recipes command refactoring [\#367](https://github.com/solvebio/solvebio-python/pull/367) ([damnjanovictanja](https://github.com/damnjanovictanja))
- Add solvebio-recipes tool [\#364](https://github.com/solvebio/solvebio-python/pull/364) ([damnjanovictanja](https://github.com/damnjanovictanja))
- Issue 324 metadata is str after saving empty dict [\#356](https://github.com/solvebio/solvebio-python/pull/356) ([nikolamaric](https://github.com/nikolamaric))
- Issue 276 dict attributes not save updates [\#355](https://github.com/solvebio/solvebio-python/pull/355) ([nikolamaric](https://github.com/nikolamaric))
- Dataset.get\_or\_create\_by\_full\_path should always return Dataset object [\#338](https://github.com/solvebio/solvebio-python/pull/338) ([jsh2134](https://github.com/jsh2134))

## [v2.12.0](https://github.com/solvebio/solvebio-python/tree/v2.12.0) (2020-08-03)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.11.0...v2.12.0)

**Fixed bugs:**

- solvebio login requires quoted arguments [\#179](https://github.com/solvebio/solvebio-python/issues/179)

**Closed issues:**

- object.tag\(\) clear existing tags in solvebio 2.11.0 [\#347](https://github.com/solvebio/solvebio-python/issues/347)
- Error on updating fields in DatasetTemplate [\#344](https://github.com/solvebio/solvebio-python/issues/344)
- Add param to disable email notifications on Dataset export [\#327](https://github.com/solvebio/solvebio-python/issues/327)

**Merged pull requests:**

- Object tagging updates [\#353](https://github.com/solvebio/solvebio-python/pull/353) ([nikolamaric](https://github.com/nikolamaric))
- Add protocol resolving logic [\#348](https://github.com/solvebio/solvebio-python/pull/348) ([nikolamaric](https://github.com/nikolamaric))
- handle case where the error message contains a list of dicts [\#343](https://github.com/solvebio/solvebio-python/pull/343) ([jsh2134](https://github.com/jsh2134))

## [v2.11.0](https://github.com/solvebio/solvebio-python/tree/v2.11.0) (2020-05-05)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.10.1...v2.11.0)

**Merged pull requests:**

- Add alpha query join \(limited left outer join\) feature [\#341](https://github.com/solvebio/solvebio-python/pull/341) ([davecap](https://github.com/davecap))
- Ability to add target fields to queries [\#340](https://github.com/solvebio/solvebio-python/pull/340) ([davecap](https://github.com/davecap))
- Add missing client pass-through for Dataset.get\_or\_create\_by\_full\_path [\#339](https://github.com/solvebio/solvebio-python/pull/339) ([davecap](https://github.com/davecap))

## [v2.10.1](https://github.com/solvebio/solvebio-python/tree/v2.10.1) (2020-04-28)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.10.0...v2.10.1)

**Fixed bugs:**

- `solvebio whoami` raises exception when no credentials are found [\#336](https://github.com/solvebio/solvebio-python/issues/336)

**Merged pull requests:**

- do not expect that error contains json [\#337](https://github.com/solvebio/solvebio-python/pull/337) ([jsh2134](https://github.com/jsh2134))

## [v2.10.0](https://github.com/solvebio/solvebio-python/tree/v2.10.0) (2020-04-24)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.9.0...v2.10.0)

**Implemented enhancements:**

- Convert `Dataset.create` calls to `Object.create` to use newer endpoint [\#326](https://github.com/solvebio/solvebio-python/issues/326)
- Show error message when requests fail with 403 [\#320](https://github.com/solvebio/solvebio-python/issues/320)
- Give Object instances that represent "datasets" the ability to be queried [\#287](https://github.com/solvebio/solvebio-python/issues/287)
- Shortcut to create a new file object in a SolveBio vault from an export [\#274](https://github.com/solvebio/solvebio-python/issues/274)
- Command line import does not support validation/reader/etc.. params from templates [\#254](https://github.com/solvebio/solvebio-python/issues/254)
- Add shortcut to use a DatasetTemplate for an import [\#245](https://github.com/solvebio/solvebio-python/issues/245)

**Fixed bugs:**

- SolveBio command line shell `--api-token` argument does not work [\#318](https://github.com/solvebio/solvebio-python/issues/318)
- Cannot log in with python-requests 2.12.4 [\#188](https://github.com/solvebio/solvebio-python/issues/188)

**Closed issues:**

- Update SolveError to include more error messages [\#333](https://github.com/solvebio/solvebio-python/issues/333)
- Request - Shortcuts for creating folders with descriptions \(or bug where create\_folder doesn't allow slashes?\) [\#251](https://github.com/solvebio/solvebio-python/issues/251)

**Merged pull requests:**

- Clean the netrc output format for the new "account" item [\#334](https://github.com/solvebio/solvebio-python/pull/334) ([davecap](https://github.com/davecap))
- More travis builds [\#332](https://github.com/solvebio/solvebio-python/pull/332) ([jsh2134](https://github.com/jsh2134))
- Object.get\_or\_create\_by\_full\_path\(\) [\#331](https://github.com/solvebio/solvebio-python/pull/331) ([jsh2134](https://github.com/jsh2134))
- add command to print out the active Task queue [\#330](https://github.com/solvebio/solvebio-python/pull/330) ([jsh2134](https://github.com/jsh2134))
- adds a shortcut to check if an object contains a tag [\#329](https://github.com/solvebio/solvebio-python/pull/329) ([jsh2134](https://github.com/jsh2134))
- CLI to download multiple files [\#328](https://github.com/solvebio/solvebio-python/pull/328) ([jsh2134](https://github.com/jsh2134))
- import command should respect template params [\#323](https://github.com/solvebio/solvebio-python/pull/323) ([jsh2134](https://github.com/jsh2134))
- More login simplification [\#322](https://github.com/solvebio/solvebio-python/pull/322) ([jsh2134](https://github.com/jsh2134))
- Updates to "create-dataset" and "import" shortcut commands [\#321](https://github.com/solvebio/solvebio-python/pull/321) ([jsh2134](https://github.com/jsh2134))
- Access token improvements [\#319](https://github.com/solvebio/solvebio-python/pull/319) ([davecap](https://github.com/davecap))

## [v2.9.0](https://github.com/solvebio/solvebio-python/tree/v2.9.0) (2019-11-07)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.8.9...v2.9.0)

**Implemented enhancements:**

- Helper shortcuts for navigating in a given folder [\#249](https://github.com/solvebio/solvebio-python/issues/249)

**Closed issues:**

- \[CLI\] Add ability to the upload shortcut to create folders if they don't exist [\#241](https://github.com/solvebio/solvebio-python/issues/241)
- \[CLI\] Make upload shortcut --full-path arg optional? [\#224](https://github.com/solvebio/solvebio-python/issues/224)

**Merged pull requests:**

- Fix error message when IP whitelisted [\#316](https://github.com/solvebio/solvebio-python/pull/316) ([davidhpark](https://github.com/davidhpark))
- Upload CLI changes, Tag CLI, vault object shortcuts [\#315](https://github.com/solvebio/solvebio-python/pull/315) ([jsh2134](https://github.com/jsh2134))
- retry on more status codes, raise error when upload unsuccessful [\#314](https://github.com/solvebio/solvebio-python/pull/314) ([jsh2134](https://github.com/jsh2134))
- Update tests reliant on deleted source data [\#313](https://github.com/solvebio/solvebio-python/pull/313) ([jsh2134](https://github.com/jsh2134))

## [v2.8.9](https://github.com/solvebio/solvebio-python/tree/v2.8.9) (2019-09-19)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.8.8...v2.8.9)

**Merged pull requests:**

- Fix issue with activity pagination [\#311](https://github.com/solvebio/solvebio-python/pull/311) ([davecap](https://github.com/davecap))
- add target\_full\_path kwarg to export shortcut [\#310](https://github.com/solvebio/solvebio-python/pull/310) ([jsh2134](https://github.com/jsh2134))

## [v2.8.8](https://github.com/solvebio/solvebio-python/tree/v2.8.8) (2019-09-12)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.8.7...v2.8.8)

**Merged pull requests:**

- add is\_shared column to saved query output [\#309](https://github.com/solvebio/solvebio-python/pull/309) ([jsh2134](https://github.com/jsh2134))
- hotfix for login when no credentials found [\#308](https://github.com/solvebio/solvebio-python/pull/308) ([jsh2134](https://github.com/jsh2134))

## [v2.8.7](https://github.com/solvebio/solvebio-python/tree/v2.8.7) (2019-09-03)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.8.6...v2.8.7)

**Fixed bugs:**

- Dash Auth defaults cookies as SameSite=Strict which blocks links to apps [\#303](https://github.com/solvebio/solvebio-python/issues/303)

**Closed issues:**

- \[Activity\] Simplify and cleanup follow\(\) function \(allow sleep time to be configured\) [\#285](https://github.com/solvebio/solvebio-python/issues/285)

**Merged pull requests:**

- Task Activity improvements [\#306](https://github.com/solvebio/solvebio-python/pull/306) ([jsh2134](https://github.com/jsh2134))

## [v2.8.6](https://github.com/solvebio/solvebio-python/tree/v2.8.6) (2019-07-03)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.8.5...v2.8.6)

**Implemented enhancements:**

- Add support for dash v1.0+ [\#278](https://github.com/solvebio/solvebio-python/issues/278)

**Merged pull requests:**

- Set cookie with SameSite=Lax to allow link-outs to Dash apps [\#304](https://github.com/solvebio/solvebio-python/pull/304) ([davecap](https://github.com/davecap))

## [v2.8.5](https://github.com/solvebio/solvebio-python/tree/v2.8.5) (2019-06-28)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.8.4...v2.8.5)

**Merged pull requests:**

- Fix typo and pop salt before passing to SolveBioAuth [\#302](https://github.com/solvebio/solvebio-python/pull/302) ([davidhpark](https://github.com/davidhpark))

## [v2.8.4](https://github.com/solvebio/solvebio-python/tree/v2.8.4) (2019-03-25)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.8.3...v2.8.4)

**Fixed bugs:**

- Installing from pypi breaks interactive shell \(urllib.parse import\)  [\#299](https://github.com/solvebio/solvebio-python/issues/299)

**Merged pull requests:**

- Use six.moves to eliminate 2to3 issues \(closes \#299\) [\#300](https://github.com/solvebio/solvebio-python/pull/300) ([davecap](https://github.com/davecap))

## [v2.8.3](https://github.com/solvebio/solvebio-python/tree/v2.8.3) (2019-03-22)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.8.2...v2.8.3)

**Fixed bugs:**

- \[DashAuth\] Specify cookie `max\_age` to prevent immediate expiry [\#296](https://github.com/solvebio/solvebio-python/issues/296)

**Merged pull requests:**

- Prevent cookie from expiring immediately [\#298](https://github.com/solvebio/solvebio-python/pull/298) ([davidhpark](https://github.com/davidhpark))

## [v2.8.2](https://github.com/solvebio/solvebio-python/tree/v2.8.2) (2019-03-07)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.8.1...v2.8.2)

**Merged pull requests:**

- Revert change to Query.facets\(\) [\#293](https://github.com/solvebio/solvebio-python/pull/293) ([davecap](https://github.com/davecap))

## [v2.8.1](https://github.com/solvebio/solvebio-python/tree/v2.8.1) (2019-03-05)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.8.0...v2.8.1)

**Implemented enhancements:**

- Retry failed S3 uploads when the connection is reset by a proxy [\#291](https://github.com/solvebio/solvebio-python/issues/291)
- \[Dash\] Add error handler in callback decorator [\#266](https://github.com/solvebio/solvebio-python/issues/266)

**Fixed bugs:**

- Calling `next` on a new Query instance breaks it [\#286](https://github.com/solvebio/solvebio-python/issues/286)
- Remove token from SolveClient repr [\#283](https://github.com/solvebio/solvebio-python/issues/283)
- \[Install\] SolveBio install fails with pycurl error re: SSL backend [\#277](https://github.com/solvebio/solvebio-python/issues/277)

**Merged pull requests:**

- Add ability for scripts to customize the user-agent [\#305](https://github.com/solvebio/solvebio-python/pull/305) ([davecap](https://github.com/davecap))
- Retry uploads up to 5 times [\#292](https://github.com/solvebio/solvebio-python/pull/292) ([davecap](https://github.com/davecap))
- Handle case where Query iterator has not been initialized \(closes \#286\) [\#288](https://github.com/solvebio/solvebio-python/pull/288) ([davecap](https://github.com/davecap))
- Dont expose the token in \_\_repr\_\_ [\#284](https://github.com/solvebio/solvebio-python/pull/284) ([davecap](https://github.com/davecap))

## [v2.8.0](https://github.com/solvebio/solvebio-python/tree/v2.8.0) (2018-10-29)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.7.0...v2.8.0)

**Implemented enhancements:**

- Remove deprecated exporters and pycurl dependency [\#281](https://github.com/solvebio/solvebio-python/issues/281)

**Merged pull requests:**

- Remove deprecated/unused exporters and remove curl dependency [\#282](https://github.com/solvebio/solvebio-python/pull/282) ([davecap](https://github.com/davecap))

## [v2.7.0](https://github.com/solvebio/solvebio-python/tree/v2.7.0) (2018-09-11)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.6.1...v2.7.0)

**Implemented enhancements:**

- Add data \(context\) to Annotator kwargs [\#271](https://github.com/solvebio/solvebio-python/issues/271)

**Merged pull requests:**

- Update Task objects and add shortcut to cancel tasks [\#273](https://github.com/solvebio/solvebio-python/pull/273) ([jsh2134](https://github.com/jsh2134))
- add annotator\_params to annotate endpoint [\#272](https://github.com/solvebio/solvebio-python/pull/272) ([jsh2134](https://github.com/jsh2134))
- add support for saving credentials with your api key [\#270](https://github.com/solvebio/solvebio-python/pull/270) ([davecap](https://github.com/davecap))

## [v2.6.1](https://github.com/solvebio/solvebio-python/tree/v2.6.1) (2018-07-10)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.6.0...v2.6.1)

**Merged pull requests:**

- fix issue with ipython embed + args [\#269](https://github.com/solvebio/solvebio-python/pull/269) ([davecap](https://github.com/davecap))

## [v2.6.0](https://github.com/solvebio/solvebio-python/tree/v2.6.0) (2018-07-10)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.5.1...v2.6.0)

**Fixed bugs:**

- \[Dash\] scripts.config.serve\_locally is set to True by default when it should be False [\#263](https://github.com/solvebio/solvebio-python/issues/263)
- \[Vaults\] create\_folder ignores path kwarg [\#260](https://github.com/solvebio/solvebio-python/issues/260)
- SolveBio shell does not see globals when defining functions [\#257](https://github.com/solvebio/solvebio-python/issues/257)
- SolveBio CLI: solvebio -\> login -\> shell does not properly retain credentials [\#255](https://github.com/solvebio/solvebio-python/issues/255)
- Iterating through a list of objects retrieved is... strange [\#250](https://github.com/solvebio/solvebio-python/issues/250)

**Merged pull requests:**

- Add Group resource [\#267](https://github.com/solvebio/solvebio-python/pull/267) ([jsh2134](https://github.com/jsh2134))
- Add saved queries [\#265](https://github.com/solvebio/solvebio-python/pull/265) ([davidhpark](https://github.com/davidhpark))
- Keep Dash scripts.config.serve\_locally False [\#264](https://github.com/solvebio/solvebio-python/pull/264) ([davidhpark](https://github.com/davidhpark))
- fix issue where API resource iterators are not reset [\#262](https://github.com/solvebio/solvebio-python/pull/262) ([davecap](https://github.com/davecap))
- Fix create\_folder shortcut [\#261](https://github.com/solvebio/solvebio-python/pull/261) ([jsh2134](https://github.com/jsh2134))
- Fix two issues with IPython shell [\#258](https://github.com/solvebio/solvebio-python/pull/258) ([davecap](https://github.com/davecap))

## [v2.5.1](https://github.com/solvebio/solvebio-python/tree/v2.5.1) (2018-05-25)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.5.0...v2.5.1)

**Implemented enhancements:**

- \[DashAuth\] Upgrade SolvBioDash and SolveBioAuth to use latest dash-auth [\#252](https://github.com/solvebio/solvebio-python/issues/252)

**Merged pull requests:**

- Add support for latest dash-auth [\#253](https://github.com/solvebio/solvebio-python/pull/253) ([davecap](https://github.com/davecap))

## [v2.5.0](https://github.com/solvebio/solvebio-python/tree/v2.5.0) (2018-04-25)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.4.6...v2.5.0)

**Implemented enhancements:**

- Ability to load filters from JSON and/or a dict [\#246](https://github.com/solvebio/solvebio-python/issues/246)

**Merged pull requests:**

- add support for loading json filters [\#248](https://github.com/solvebio/solvebio-python/pull/248) ([davecap](https://github.com/davecap))

## [v2.4.6](https://github.com/solvebio/solvebio-python/tree/v2.4.6) (2018-02-23)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.4.5...v2.4.6)

**Closed issues:**

- Unable to upload to cross-account Vault  [\#238](https://github.com/solvebio/solvebio-python/issues/238)
- Problem logging in using Python 3.6 [\#235](https://github.com/solvebio/solvebio-python/issues/235)

**Merged pull requests:**

- pass vault object through instead of vault name [\#239](https://github.com/solvebio/solvebio-python/pull/239) ([jsh2134](https://github.com/jsh2134))
- printing incorrect url [\#237](https://github.com/solvebio/solvebio-python/pull/237) ([jsh2134](https://github.com/jsh2134))
- removed six import, changed input to raw\_input [\#236](https://github.com/solvebio/solvebio-python/pull/236) ([davidhpark](https://github.com/davidhpark))

## [v2.4.5](https://github.com/solvebio/solvebio-python/tree/v2.4.5) (2018-02-13)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.4.4...v2.4.5)

**Merged pull requests:**

- fix client-passthrough for object validation [\#234](https://github.com/solvebio/solvebio-python/pull/234) ([davecap](https://github.com/davecap))

## [v2.4.4](https://github.com/solvebio/solvebio-python/tree/v2.4.4) (2018-02-12)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.4.3...v2.4.4)

**Fixed bugs:**

- Fix error message shown in "validate\_full\_path" when not authenticated [\#232](https://github.com/solvebio/solvebio-python/issues/232)

**Merged pull requests:**

- fix error message and client pass-through for object path validation [\#233](https://github.com/solvebio/solvebio-python/pull/233) ([davecap](https://github.com/davecap))

## [v2.4.3](https://github.com/solvebio/solvebio-python/tree/v2.4.3) (2018-02-08)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.4.2...v2.4.3)

**Closed issues:**

- Confusing error on dataset creation if there is a folder with the same name in that folder path [\#229](https://github.com/solvebio/solvebio-python/issues/229)

**Merged pull requests:**

- include additional oauth error response content in the view [\#231](https://github.com/solvebio/solvebio-python/pull/231) ([davecap](https://github.com/davecap))
- include optional object type assertion when getting objects [\#230](https://github.com/solvebio/solvebio-python/pull/230) ([davecap](https://github.com/davecap))

## [v2.4.2](https://github.com/solvebio/solvebio-python/tree/v2.4.2) (2018-02-01)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.4.1...v2.4.2)

**Implemented enhancements:**

- \[Manifest\] Add reader\_params to add\_url [\#214](https://github.com/solvebio/solvebio-python/issues/214)

**Merged pull requests:**

- Fix issue where files were not uploaded in binary mode [\#228](https://github.com/solvebio/solvebio-python/pull/228) ([davecap](https://github.com/davecap))
- allow login\(api\_host=XYZ\) [\#225](https://github.com/solvebio/solvebio-python/pull/225) ([davecap](https://github.com/davecap))
- add reader\_params [\#216](https://github.com/solvebio/solvebio-python/pull/216) ([jsh2134](https://github.com/jsh2134))

## [v2.4.1](https://github.com/solvebio/solvebio-python/tree/v2.4.1) (2018-01-16)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.4.0...v2.4.1)

**Fixed bugs:**

- "Jobs" URL shown when importing a file is incorrect [\#183](https://github.com/solvebio/solvebio-python/issues/183)

**Closed issues:**

- \[Export\] Filenames contain AWS file parameters [\#208](https://github.com/solvebio/solvebio-python/issues/208)
- \[Upload\] Shortcut fails when folder name contains space? [\#201](https://github.com/solvebio/solvebio-python/issues/201)
- Python fix-ups [\#182](https://github.com/solvebio/solvebio-python/issues/182)

**Merged pull requests:**

- better error if invalid path [\#223](https://github.com/solvebio/solvebio-python/pull/223) ([jsh2134](https://github.com/jsh2134))
- shortcuts properly handle ~ autoexpand [\#222](https://github.com/solvebio/solvebio-python/pull/222) ([jsh2134](https://github.com/jsh2134))
- minor fixes [\#221](https://github.com/solvebio/solvebio-python/pull/221) ([jsh2134](https://github.com/jsh2134))
- fix filename issue for downloadable resource [\#220](https://github.com/solvebio/solvebio-python/pull/220) ([davecap](https://github.com/davecap))
- validate the object's full path before getting it by full path [\#219](https://github.com/solvebio/solvebio-python/pull/219) ([davecap](https://github.com/davecap))

## [v2.4.0](https://github.com/solvebio/solvebio-python/tree/v2.4.0) (2018-01-11)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.3.3...v2.4.0)

**Merged pull requests:**

- try refactoring path validators with regex [\#218](https://github.com/solvebio/solvebio-python/pull/218) ([davecap](https://github.com/davecap))
- update import and create-dataset shortcuts to require full path [\#217](https://github.com/solvebio/solvebio-python/pull/217) ([jsh2134](https://github.com/jsh2134))
- remove invalid tabulate fields for Application resource [\#215](https://github.com/solvebio/solvebio-python/pull/215) ([davecap](https://github.com/davecap))

## [v2.3.3](https://github.com/solvebio/solvebio-python/tree/v2.3.3) (2017-12-13)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.3.2...v2.3.3)

**Fixed bugs:**

- Unable to download Vault Objects [\#212](https://github.com/solvebio/solvebio-python/issues/212)
- Dash auth wrapper redirect URL is incorrect if different from provided app\_url [\#210](https://github.com/solvebio/solvebio-python/issues/210)
- File upload with version 2.1.0 on Windows 7 [\#189](https://github.com/solvebio/solvebio-python/issues/189)

**Closed issues:**

- Deploy v2.3.2 to pypi [\#207](https://github.com/solvebio/solvebio-python/issues/207)

**Merged pull requests:**

- add DownloadableAPIResource mixin to Object resource and add support for Object download response to the mixin [\#213](https://github.com/solvebio/solvebio-python/pull/213) ([davecap](https://github.com/davecap))
- add required args to create\_folder and create\_dataset [\#209](https://github.com/solvebio/solvebio-python/pull/209) ([davecap](https://github.com/davecap))
- use cross-platform /dev/null \(closes \#189\) [\#190](https://github.com/solvebio/solvebio-python/pull/190) ([davecap](https://github.com/davecap))

## [v2.3.2](https://github.com/solvebio/solvebio-python/tree/v2.3.2) (2017-11-28)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.3.1...v2.3.2)

**Closed issues:**

- Release Version 2.3.1 to pypi [\#205](https://github.com/solvebio/solvebio-python/issues/205)

## [v2.3.1](https://github.com/solvebio/solvebio-python/tree/v2.3.1) (2017-11-22)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.3.0...v2.3.1)

**Merged pull requests:**

- update retrieval of datasets by jobs/tasks [\#204](https://github.com/solvebio/solvebio-python/pull/204) ([jsh2134](https://github.com/jsh2134))
- replace PRINTABLE\_NAME with something dynamic [\#203](https://github.com/solvebio/solvebio-python/pull/203) ([davecap](https://github.com/davecap))

## [v2.3.0](https://github.com/solvebio/solvebio-python/tree/v2.3.0) (2017-11-09)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.2.1...v2.3.0)

**Implemented enhancements:**

- Add support for entity filters in Query class [\#195](https://github.com/solvebio/solvebio-python/issues/195)

**Merged pull requests:**

- add support for entities query param \(closes \#195\) [\#202](https://github.com/solvebio/solvebio-python/pull/202) ([davecap](https://github.com/davecap))
- add Application resource [\#200](https://github.com/solvebio/solvebio-python/pull/200) ([davecap](https://github.com/davecap))

## [v2.2.1](https://github.com/solvebio/solvebio-python/tree/v2.2.1) (2017-10-18)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.2.0...v2.2.1)

**Fixed bugs:**

- Task resource does not use local SolveClient [\#197](https://github.com/solvebio/solvebio-python/issues/197)

**Merged pull requests:**

- use the provided app\_url instead of flask's url\_root \(fixes \#210\) [\#211](https://github.com/solvebio/solvebio-python/pull/211) ([davecap](https://github.com/davecap))
- \[Bug\] method turned property bug [\#206](https://github.com/solvebio/solvebio-python/pull/206) ([jsh2134](https://github.com/jsh2134))
- fix issue where task method did not pass client through [\#198](https://github.com/solvebio/solvebio-python/pull/198) ([davecap](https://github.com/davecap))

## [v2.2.0](https://github.com/solvebio/solvebio-python/tree/v2.2.0) (2017-10-05)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.1.0...v2.2.0)

**Fixed bugs:**

- incorrect filter parameter [\#192](https://github.com/solvebio/solvebio-python/pull/192) ([jsh2134](https://github.com/jsh2134))

**Merged pull requests:**

- update sample script [\#196](https://github.com/solvebio/solvebio-python/pull/196) ([jsh2134](https://github.com/jsh2134))
- update manifest info [\#193](https://github.com/solvebio/solvebio-python/pull/193) ([jsh2134](https://github.com/jsh2134))
- Support for isolated SolveClient \(with non-global tokens\) [\#191](https://github.com/solvebio/solvebio-python/pull/191) ([davecap](https://github.com/davecap))

## [v2.1.0](https://github.com/solvebio/solvebio-python/tree/v2.1.0) (2017-09-08)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.0.1...v2.1.0)

**Closed issues:**

- Add beacon and beacon set support [\#184](https://github.com/solvebio/solvebio-python/issues/184)

**Merged pull requests:**

- Use Object based uploads, deprecate Upload resource [\#186](https://github.com/solvebio/solvebio-python/pull/186) ([jsh2134](https://github.com/jsh2134))
- add basic BeaconSet and Beacon resources [\#185](https://github.com/solvebio/solvebio-python/pull/185) ([davecap](https://github.com/davecap))

## [v2.0.1](https://github.com/solvebio/solvebio-python/tree/v2.0.1) (2017-08-23)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v2.0.0...v2.0.1)

**Merged pull requests:**

- update filter creation to correctly handle nested dict filters [\#180](https://github.com/solvebio/solvebio-python/pull/180) ([jsh2134](https://github.com/jsh2134))

## [v2.0.0](https://github.com/solvebio/solvebio-python/tree/v2.0.0) (2017-07-28)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.17.1...v2.0.0)

**Implemented enhancements:**

- When an export is complete, add a message to indicate that the user should download the file [\#164](https://github.com/solvebio/solvebio-python/issues/164)
- Allow `solvebio import` shortcut to take an upload id [\#120](https://github.com/solvebio/solvebio-python/issues/120)
- HTTP Caching support for data query requests [\#11](https://github.com/solvebio/solvebio-python/issues/11)

**Fixed bugs:**

- Check for existence in depository.latest\_version\(\) [\#124](https://github.com/solvebio/solvebio-python/issues/124)

**Closed issues:**

- Add "upload" command-line sub-command [\#149](https://github.com/solvebio/solvebio-python/issues/149)
- Autocomplete on query filters \(kwargs\)? [\#4](https://github.com/solvebio/solvebio-python/issues/4)

**Merged pull requests:**

- Hyrule Support for Python Client [\#172](https://github.com/solvebio/solvebio-python/pull/172) ([jhuttner](https://github.com/jhuttner))

## [v1.17.1](https://github.com/solvebio/solvebio-python/tree/v1.17.1) (2017-06-05)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.17.0...v1.17.1)

**Implemented enhancements:**

- Add Unit Tests for client shortcuts [\#142](https://github.com/solvebio/solvebio-python/issues/142)

**Fixed bugs:**

- Dataset export of a query requires a limit [\#167](https://github.com/solvebio/solvebio-python/issues/167)

**Closed issues:**

- Add a "data migration preview" mode to test migrations \("dry-run"\) [\#161](https://github.com/solvebio/solvebio-python/issues/161)
- Check compatibility with Travis Build environment updates [\#158](https://github.com/solvebio/solvebio-python/issues/158)

**Merged pull requests:**

- use new travis distribution: Ubuntu 14 [\#171](https://github.com/solvebio/solvebio-python/pull/171) ([jsh2134](https://github.com/jsh2134))
- Test case updates [\#170](https://github.com/solvebio/solvebio-python/pull/170) ([jsh2134](https://github.com/jsh2134))
- handle max export limit case [\#169](https://github.com/solvebio/solvebio-python/pull/169) ([jsh2134](https://github.com/jsh2134))

## [v1.17.0](https://github.com/solvebio/solvebio-python/tree/v1.17.0) (2017-05-04)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.16.0...v1.17.0)

**Closed issues:**

- Add support for Expressions and Annotations [\#146](https://github.com/solvebio/solvebio-python/issues/146)

**Merged pull requests:**

- Add Annotator and Expression support [\#163](https://github.com/solvebio/solvebio-python/pull/163) ([davecap](https://github.com/davecap))
- fix an issue where a manually set api\_host was not used by client [\#162](https://github.com/solvebio/solvebio-python/pull/162) ([davecap](https://github.com/davecap))
- mock create dataset test [\#160](https://github.com/solvebio/solvebio-python/pull/160) ([jsh2134](https://github.com/jsh2134))
- fix the last message on DatasetMigration.follow\(\) [\#159](https://github.com/solvebio/solvebio-python/pull/159) ([davecap](https://github.com/davecap))

## [v1.16.0](https://github.com/solvebio/solvebio-python/tree/v1.16.0) (2017-04-21)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.15.4...v1.16.0)

**Implemented enhancements:**

- Clone/copy shortcut based on a query [\#145](https://github.com/solvebio/solvebio-python/issues/145)
- Add `exclude\_fields` support to Query [\#148](https://github.com/solvebio/solvebio-python/issues/148)
- Add retries to the Upload resource [\#147](https://github.com/solvebio/solvebio-python/issues/147)
- More robust follow\(\) function [\#134](https://github.com/solvebio/solvebio-python/issues/134)

**Fixed bugs:**

- Update DatasetImport follow\(\) function to follow DatasetCommits as well [\#133](https://github.com/solvebio/solvebio-python/issues/133)

**Closed issues:**

- Add support for Dataset Migrations [\#151](https://github.com/solvebio/solvebio-python/issues/151)
- Add support for dataset exports [\#150](https://github.com/solvebio/solvebio-python/issues/150)

**Merged pull requests:**

- update follow logic of imports now the commits are decoupled [\#157](https://github.com/solvebio/solvebio-python/pull/157) ([jsh2134](https://github.com/jsh2134))
- Add built-in connection retries using a request session [\#156](https://github.com/solvebio/solvebio-python/pull/156) ([davecap](https://github.com/davecap))
- add DatasetMigration resource and migrate functions for Query and Dataset [\#155](https://github.com/solvebio/solvebio-python/pull/155) ([davecap](https://github.com/davecap))
- Add support for DatasetExports [\#154](https://github.com/solvebio/solvebio-python/pull/154) ([davecap](https://github.com/davecap))
- add exclude\_fields param to Query \(closes \#148\) [\#153](https://github.com/solvebio/solvebio-python/pull/153) ([davecap](https://github.com/davecap))
- Add retries to Upload creation \(fixes \#147\) [\#152](https://github.com/solvebio/solvebio-python/pull/152) ([davecap](https://github.com/davecap))

## [v1.15.4](https://github.com/solvebio/solvebio-python/tree/v1.15.4) (2017-03-15)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.15.3...v1.15.4)

**Merged pull requests:**

- include randint in deponame also [\#144](https://github.com/solvebio/solvebio-python/pull/144) ([jsh2134](https://github.com/jsh2134))

## [v1.15.3](https://github.com/solvebio/solvebio-python/tree/v1.15.3) (2017-03-15)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.15.2...v1.15.3)

**Closed issues:**

- Import shortcut isn't playing well with the new capacity argument [\#139](https://github.com/solvebio/solvebio-python/issues/139)

**Merged pull requests:**

- add more python 3 versions [\#143](https://github.com/solvebio/solvebio-python/pull/143) ([jsh2134](https://github.com/jsh2134))
- fix issue where template fields were not used in dataset creation [\#141](https://github.com/solvebio/solvebio-python/pull/141) ([davecap](https://github.com/davecap))
- Fix capacity argument in import dataset command [\#140](https://github.com/solvebio/solvebio-python/pull/140) ([davecap](https://github.com/davecap))

## [v1.15.2](https://github.com/solvebio/solvebio-python/tree/v1.15.2) (2017-03-14)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.15.1...v1.15.2)

**Merged pull requests:**

- fix an issue where the CLI was ignoring env var or other default api\_key [\#138](https://github.com/solvebio/solvebio-python/pull/138) ([davecap](https://github.com/davecap))

## [v1.15.1](https://github.com/solvebio/solvebio-python/tree/v1.15.1) (2017-03-12)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.15.0...v1.15.1)

**Implemented enhancements:**

- Add commit\_mode details to -h help [\#136](https://github.com/solvebio/solvebio-python/issues/136)
- Allow `solvebio import` to take a dataset capacity argument [\#135](https://github.com/solvebio/solvebio-python/issues/135)

**Closed issues:**

- Problem installing solvebio client - curl-config not found [\#131](https://github.com/solvebio/solvebio-python/issues/131)
- Can not import without a template in \(update-genome branch\) [\#127](https://github.com/solvebio/solvebio-python/issues/127)

**Merged pull requests:**

- add capacity argument to create-dataset command \(closes \#135\) [\#137](https://github.com/solvebio/solvebio-python/pull/137) ([davecap](https://github.com/davecap))
- Provide help message on curl-config error \(\#131\) [\#132](https://github.com/solvebio/solvebio-python/pull/132) ([jhuttner](https://github.com/jhuttner))
- some error responses were not being parsed correctly; this simplifies [\#130](https://github.com/solvebio/solvebio-python/pull/130) ([davecap](https://github.com/davecap))
- import shortcut examples [\#129](https://github.com/solvebio/solvebio-python/pull/129) ([dandanxu](https://github.com/dandanxu))
- add commit mode as an import option [\#128](https://github.com/solvebio/solvebio-python/pull/128) ([jsh2134](https://github.com/jsh2134))
- update genome builds upon get\_or\_create, add new create-dataset command [\#126](https://github.com/solvebio/solvebio-python/pull/126) ([davecap](https://github.com/davecap))
- add invalid file path name in error  [\#122](https://github.com/solvebio/solvebio-python/pull/122) ([jsh2134](https://github.com/jsh2134))

## [v1.15.0](https://github.com/solvebio/solvebio-python/tree/v1.15.0) (2016-12-19)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.14.2...v1.15.0)

**Implemented enhancements:**

- Display upload percentage for file uploads [\#119](https://github.com/solvebio/solvebio-python/issues/119)

**Merged pull requests:**

- add file wrapper to show upload progress bar \(closes \#119\) [\#123](https://github.com/solvebio/solvebio-python/pull/123) ([davecap](https://github.com/davecap))
- fix issue where solvebio cli did not open in python3 [\#121](https://github.com/solvebio/solvebio-python/pull/121) ([davecap](https://github.com/davecap))
- remove trailing commas that broke things, read GZipped template files [\#118](https://github.com/solvebio/solvebio-python/pull/118) ([jsh2134](https://github.com/jsh2134))

## [v1.14.2](https://github.com/solvebio/solvebio-python/tree/v1.14.2) (2016-12-13)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.14.1...v1.14.2)

## [v1.14.1](https://github.com/solvebio/solvebio-python/tree/v1.14.1) (2016-12-12)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.14.0...v1.14.1)

**Merged pull requests:**

- create datasets with a template file or without a template at all [\#117](https://github.com/solvebio/solvebio-python/pull/117) ([jsh2134](https://github.com/jsh2134))
- add support for query ordering param \(closes \#114\) [\#116](https://github.com/solvebio/solvebio-python/pull/116) ([davecap](https://github.com/davecap))
- add simple manifest upload example [\#113](https://github.com/solvebio/solvebio-python/pull/113) ([jsh2134](https://github.com/jsh2134))

## [v1.14.0](https://github.com/solvebio/solvebio-python/tree/v1.14.0) (2016-12-05)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.13.6...v1.14.0)

**Implemented enhancements:**

- Add ordering param for dataset queries [\#114](https://github.com/solvebio/solvebio-python/issues/114)

**Fixed bugs:**

- \[Export\] Export should support the query fields parameter instead of always exporting all fields [\#91](https://github.com/solvebio/solvebio-python/issues/91)

**Merged pull requests:**

- add JSON exporter for queries [\#115](https://github.com/solvebio/solvebio-python/pull/115) ([davecap](https://github.com/davecap))
- First example Python script [\#112](https://github.com/solvebio/solvebio-python/pull/112) ([dandanxu](https://github.com/dandanxu))
- Flat CSV Exporter [\#95](https://github.com/solvebio/solvebio-python/pull/95) ([jercoh](https://github.com/jercoh))

## [v1.13.6](https://github.com/solvebio/solvebio-python/tree/v1.13.6) (2016-10-27)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.13.5...v1.13.6)

**Merged pull requests:**

- handle case where no results are returned in the list object [\#111](https://github.com/solvebio/solvebio-python/pull/111) ([davecap](https://github.com/davecap))
- use pyvcf built-in file extension detection and gzip support [\#110](https://github.com/solvebio/solvebio-python/pull/110) ([davecap](https://github.com/davecap))

## [v1.13.5](https://github.com/solvebio/solvebio-python/tree/v1.13.5) (2016-09-15)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.13.4...v1.13.5)

**Merged pull requests:**

- fix the vcf parser for python3 [\#109](https://github.com/solvebio/solvebio-python/pull/109) ([davecap](https://github.com/davecap))
- add support for specialized SnpEff ANN field parsing [\#108](https://github.com/solvebio/solvebio-python/pull/108) ([davecap](https://github.com/davecap))

## [v1.13.4](https://github.com/solvebio/solvebio-python/tree/v1.13.4) (2016-08-25)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.13.3...v1.13.4)

**Merged pull requests:**

- add SolveBio variant ID to VCF to JSON parser output [\#107](https://github.com/solvebio/solvebio-python/pull/107) ([davecap](https://github.com/davecap))

## [v1.13.3](https://github.com/solvebio/solvebio-python/tree/v1.13.3) (2016-08-11)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.13.2...v1.13.3)

**Closed issues:**

- \[Manifest\] Add\(\) not allowing URLs [\#105](https://github.com/solvebio/solvebio-python/issues/105)

**Merged pull requests:**

- expanduser not expandpath \(fixes \#105\) [\#106](https://github.com/solvebio/solvebio-python/pull/106) ([davecap](https://github.com/davecap))

## [v1.13.2](https://github.com/solvebio/solvebio-python/tree/v1.13.2) (2016-08-03)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.13.1...v1.13.2)

**Implemented enhancements:**

- Filter by number of items in a field [\#54](https://github.com/solvebio/solvebio-python/issues/54)

**Fixed bugs:**

- Depositories, depository versions, and datasets are not deletable [\#102](https://github.com/solvebio/solvebio-python/issues/102)

**Closed issues:**

- \[Manifest\] Add\(\) not allowing my local filepath [\#101](https://github.com/solvebio/solvebio-python/issues/101)

**Merged pull requests:**

- expanduser prior to checking ispath or isdir in manifest \(fixes \#101\) [\#104](https://github.com/solvebio/solvebio-python/pull/104) ([davecap](https://github.com/davecap))
- makes datasets, depository versions, and depositories deletable [\#103](https://github.com/solvebio/solvebio-python/pull/103) ([davecap](https://github.com/davecap))
- Add expanding vcf parser as a contrib module [\#100](https://github.com/solvebio/solvebio-python/pull/100) ([davecap](https://github.com/davecap))

## [v1.13.1](https://github.com/solvebio/solvebio-python/tree/v1.13.1) (2016-06-03)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.13.0...v1.13.1)

## [v1.13.0](https://github.com/solvebio/solvebio-python/tree/v1.13.0) (2016-06-03)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.12.1...v1.13.0)

**Merged pull requests:**

- Refactor subcommand arguments; add simple dataset import subcommand [\#99](https://github.com/solvebio/solvebio-python/pull/99) ([davecap](https://github.com/davecap))

## [v1.12.1](https://github.com/solvebio/solvebio-python/tree/v1.12.1) (2016-05-12)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.12.0...v1.12.1)

**Fixed bugs:**

- \[Windows\] Fix login mechanism on Windows \($HOME not set\) [\#97](https://github.com/solvebio/solvebio-python/issues/97)

**Merged pull requests:**

- use expanduser instead of looking for $HOME manually \(fixes \#97\) [\#98](https://github.com/solvebio/solvebio-python/pull/98) ([davecap](https://github.com/davecap))

## [v1.12.0](https://github.com/solvebio/solvebio-python/tree/v1.12.0) (2016-05-10)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.11.0...v1.12.0)

**Merged pull requests:**

- Add support for uploads and imports [\#96](https://github.com/solvebio/solvebio-python/pull/96) ([davecap](https://github.com/davecap))

## [v1.11.0](https://github.com/solvebio/solvebio-python/tree/v1.11.0) (2016-03-28)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.10.0...v1.11.0)

**Fixed bugs:**

- Add support for login domains [\#93](https://github.com/solvebio/solvebio-python/issues/93)

**Merged pull requests:**

- adds domain support to login cli \(fixes \#93\) [\#94](https://github.com/solvebio/solvebio-python/pull/94) ([davecap](https://github.com/davecap))

## [v1.10.0](https://github.com/solvebio/solvebio-python/tree/v1.10.0) (2016-03-07)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.9.1...v1.10.0)

**Merged pull requests:**

- Adds Dataset bulk export helper/verification code [\#92](https://github.com/solvebio/solvebio-python/pull/92) ([davecap](https://github.com/davecap))

## [v1.9.1](https://github.com/solvebio/solvebio-python/tree/v1.9.1) (2016-02-10)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.9.0...v1.9.1)

**Merged pull requests:**

- add XLSX exporter [\#90](https://github.com/solvebio/solvebio-python/pull/90) ([davecap](https://github.com/davecap))
- Recursively process listed, nested dicts [\#89](https://github.com/solvebio/solvebio-python/pull/89) ([davecap](https://github.com/davecap))
- Adds export functionality closes \#3 [\#88](https://github.com/solvebio/solvebio-python/pull/88) ([davecap](https://github.com/davecap))
- test\_cases\_changelog [\#84](https://github.com/solvebio/solvebio-python/pull/84) ([eyalfoni](https://github.com/eyalfoni))

## [v1.9.0](https://github.com/solvebio/solvebio-python/tree/v1.9.0) (2016-02-01)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.8.1...v1.9.0)

**Implemented enhancements:**

- Add support for record lookups to Dataset resource [\#81](https://github.com/solvebio/solvebio-python/issues/81)

**Fixed bugs:**

- Queries are evaluated twice on failure in some cases [\#78](https://github.com/solvebio/solvebio-python/issues/78)
- Unicode displaying in dataset descriptions [\#56](https://github.com/solvebio/solvebio-python/issues/56)

**Closed issues:**

- Add test coverage for changelog requests [\#83](https://github.com/solvebio/solvebio-python/issues/83)
- Add test coverage for beacon requests [\#82](https://github.com/solvebio/solvebio-python/issues/82)
- API Key Login not registering? [\#80](https://github.com/solvebio/solvebio-python/issues/80)
- print statement not working in Python 2.7.6 unless wrapped in \(\) [\#79](https://github.com/solvebio/solvebio-python/issues/79)
- Convert old style string replacement with .format\(\) [\#8](https://github.com/solvebio/solvebio-python/issues/8)
- Local datastore bindings for import & export [\#3](https://github.com/solvebio/solvebio-python/issues/3)

**Merged pull requests:**

- fixes a bug where Query buffering didn't always use the slice starting offset [\#87](https://github.com/solvebio/solvebio-python/pull/87) ([davecap](https://github.com/davecap))
- added sbid lookup support in datasets - closes \#81 [\#86](https://github.com/solvebio/solvebio-python/pull/86) ([eyalfoni](https://github.com/eyalfoni))
- fixes multiple queries with wrong filter closes \#78 [\#85](https://github.com/solvebio/solvebio-python/pull/85) ([eyalfoni](https://github.com/eyalfoni))

## [v1.8.1](https://github.com/solvebio/solvebio-python/tree/v1.8.1) (2015-07-22)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.8.0...v1.8.1)

## [v1.8.0](https://github.com/solvebio/solvebio-python/tree/v1.8.0) (2015-07-14)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.7.11...v1.8.0)

**Closed issues:**

- Python booleans not supported in filters [\#75](https://github.com/solvebio/solvebio-python/issues/75)

**Merged pull requests:**

- Adds Python3 support [\#77](https://github.com/solvebio/solvebio-python/pull/77) ([davecap](https://github.com/davecap))

## [v1.7.11](https://github.com/solvebio/solvebio-python/tree/v1.7.11) (2015-03-26)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/v1.7.10...v1.7.11)

**Merged pull requests:**

- Add beacon and changelog endpoints [\#76](https://github.com/solvebio/solvebio-python/pull/76) ([jsh2134](https://github.com/jsh2134))

## [v1.7.10](https://github.com/solvebio/solvebio-python/tree/v1.7.10) (2015-03-12)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.7.9...v1.7.10)

## [1.7.9](https://github.com/solvebio/solvebio-python/tree/1.7.9) (2015-02-18)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.7.7...1.7.9)

## [1.7.7](https://github.com/solvebio/solvebio-python/tree/1.7.7) (2015-02-04)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.7.8...1.7.7)

## [1.7.8](https://github.com/solvebio/solvebio-python/tree/1.7.8) (2015-02-04)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.7.6...1.7.8)

## [1.7.6](https://github.com/solvebio/solvebio-python/tree/1.7.6) (2015-01-29)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.7.5...1.7.6)

## [1.7.5](https://github.com/solvebio/solvebio-python/tree/1.7.5) (2015-01-26)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.7.4...1.7.5)

**Implemented enhancements:**

- Easy way to pull out latest available datasets for retrieval in the API [\#55](https://github.com/solvebio/solvebio-python/issues/55)

**Merged pull requests:**

- improve performance when combining Filters; make it easier to get api\_key from local credentials [\#74](https://github.com/solvebio/solvebio-python/pull/74) ([davecap](https://github.com/davecap))

## [1.7.4](https://github.com/solvebio/solvebio-python/tree/1.7.4) (2014-12-23)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.7.3...1.7.4)

## [1.7.3](https://github.com/solvebio/solvebio-python/tree/1.7.3) (2014-12-18)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.7.2...1.7.3)

## [1.7.2](https://github.com/solvebio/solvebio-python/tree/1.7.2) (2014-12-15)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.7.1...1.7.2)

**Merged pull requests:**

- Feature/query refactor [\#73](https://github.com/solvebio/solvebio-python/pull/73) ([davecap](https://github.com/davecap))

## [1.7.1](https://github.com/solvebio/solvebio-python/tree/1.7.1) (2014-12-08)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.7.0...1.7.1)

**Fixed bugs:**

- List index out of range error when looping through query [\#67](https://github.com/solvebio/solvebio-python/issues/67)

## [1.7.0](https://github.com/solvebio/solvebio-python/tree/1.7.0) (2014-11-28)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.6.1...1.7.0)

**Implemented enhancements:**

- Handle API rate-limiting in the client [\#60](https://github.com/solvebio/solvebio-python/issues/60)
- Should show a IPaddress/message at launch, if the python-client is not connected to api.solvebio.com [\#59](https://github.com/solvebio/solvebio-python/issues/59)
- On local API, shows "You are not logged in" even if API\_KEY and API\_HOST are set up. [\#58](https://github.com/solvebio/solvebio-python/issues/58)
- client-side warning for long-iterating queries [\#53](https://github.com/solvebio/solvebio-python/issues/53)
- Pretty print the output of `Dataset.fields\(\)` [\#49](https://github.com/solvebio/solvebio-python/issues/49)
- Add len\(\) and iteration to ListableAPIResource [\#38](https://github.com/solvebio/solvebio-python/issues/38)
- Pretty printing of resources like depos/versions/datasets/field lists/facets [\#5](https://github.com/solvebio/solvebio-python/issues/5)

**Fixed bugs:**

- Auth credentials error [\#72](https://github.com/solvebio/solvebio-python/issues/72)
- not specifying protocol in SOLVEBIO\_API\_HOST breaks login [\#70](https://github.com/solvebio/solvebio-python/issues/70)
- Query \_\_repr\_\_ [\#62](https://github.com/solvebio/solvebio-python/issues/62)
- count\(\) always returns 0 when limit=0 [\#61](https://github.com/solvebio/solvebio-python/issues/61)
- make `paging=True` the default [\#52](https://github.com/solvebio/solvebio-python/issues/52)
- fix `limit` semantics [\#51](https://github.com/solvebio/solvebio-python/issues/51)

**Closed issues:**

- add support for .count\(\) [\#50](https://github.com/solvebio/solvebio-python/issues/50)
- solvebio login shows unusual email default [\#47](https://github.com/solvebio/solvebio-python/issues/47)
- initial double-querying [\#22](https://github.com/solvebio/solvebio-python/issues/22)
- "Cannot detect terminal column width" error in ipython notebooks [\#21](https://github.com/solvebio/solvebio-python/issues/21)

**Merged pull requests:**

- API host url validation;closes \#70 [\#71](https://github.com/solvebio/solvebio-python/pull/71) ([pgeez](https://github.com/pgeez))
- Feature/hotfix 67 [\#69](https://github.com/solvebio/solvebio-python/pull/69) ([pgeez](https://github.com/pgeez))
- ListableAPIResources are tabulatable. Set class variable TAB\_FIELDS to specify a subset of fields. \_\_init\_\_.py: Don't need whomi, login, or logout in \_\_main\_\_ Split depository test from depositoryversion test [\#66](https://github.com/solvebio/solvebio-python/pull/66) ([rocky](https://github.com/rocky))
- add new GenomicFilter for range and position filters on genomic datasets [\#65](https://github.com/solvebio/solvebio-python/pull/65) ([davecap](https://github.com/davecap))
- Rework login. Don't store credentials in .netrc. [\#64](https://github.com/solvebio/solvebio-python/pull/64) ([rocky](https://github.com/rocky))
- Redo how len\(\) works. len\(\) is number of things one can iterate over. .count\(\) is the total number of items. The old "paging" mode is no more, although one can still set a "page\_size". [\#63](https://github.com/solvebio/solvebio-python/pull/63) ([rocky](https://github.com/rocky))
- tabulate dataset fields in printing \(\_\_str\_\_\) [\#57](https://github.com/solvebio/solvebio-python/pull/57) ([rocky](https://github.com/rocky))

## [1.6.1](https://github.com/solvebio/solvebio-python/tree/1.6.1) (2014-11-03)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.6.0...1.6.1)

**Implemented enhancements:**

- easier way to logout [\#42](https://github.com/solvebio/solvebio-python/issues/42)

**Fixed bugs:**

- iPython notebook printing output to terminal instead of screen [\#43](https://github.com/solvebio/solvebio-python/issues/43)

**Merged pull requests:**

- \_ask\_for\_credentials: default\_email is put in prompt \*only\* if it is str... [\#48](https://github.com/solvebio/solvebio-python/pull/48) ([rocky](https://github.com/rocky))
- Inside solvebio shell allow solvebio.Dataset, solvebio.Depository..., tabulate [\#32](https://github.com/solvebio/solvebio-python/pull/32) ([rocky](https://github.com/rocky))

## [1.6.0](https://github.com/solvebio/solvebio-python/tree/1.6.0) (2014-10-31)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.5.2...1.6.0)

**Closed issues:**

- Weird error message when giving password when logging in [\#41](https://github.com/solvebio/solvebio-python/issues/41)

**Merged pull requests:**

- Address issue \#43 and possibly \#21 [\#46](https://github.com/solvebio/solvebio-python/pull/46) ([rocky](https://github.com/rocky))
- Login/Logout via IPython [\#45](https://github.com/solvebio/solvebio-python/pull/45) ([rocky](https://github.com/rocky))
- Depository, DepositoryVersion, Dataset, DatasetField tests. Note: also [\#40](https://github.com/solvebio/solvebio-python/pull/40) ([rocky](https://github.com/rocky))
- Travis testing on Python 2.6 [\#39](https://github.com/solvebio/solvebio-python/pull/39) ([rocky](https://github.com/rocky))
- Add Annotate and Sample download; some refactoring [\#37](https://github.com/solvebio/solvebio-python/pull/37) ([rocky](https://github.com/rocky))
- Feature/annotate download part2 [\#36](https://github.com/solvebio/solvebio-python/pull/36) ([rocky](https://github.com/rocky))
- Add flake8 testing from travis [\#35](https://github.com/solvebio/solvebio-python/pull/35) ([rocky](https://github.com/rocky))
- Feature/annotate broken [\#31](https://github.com/solvebio/solvebio-python/pull/31) ([rocky](https://github.com/rocky))
- Sync what we have. There will be a few more updates... [\#30](https://github.com/solvebio/solvebio-python/pull/30) ([rocky](https://github.com/rocky))
- Redo tabulate sorting to add as a parameter. [\#28](https://github.com/solvebio/solvebio-python/pull/28) ([rocky](https://github.com/rocky))
- Tabulate sort [\#27](https://github.com/solvebio/solvebio-python/pull/27) ([rocky](https://github.com/rocky))
- Tabulate [\#26](https://github.com/solvebio/solvebio-python/pull/26) ([rocky](https://github.com/rocky))

## [1.5.2](https://github.com/solvebio/solvebio-python/tree/1.5.2) (2014-09-25)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.5.1...1.5.2)

**Merged pull requests:**

- Makefile [\#24](https://github.com/solvebio/solvebio-python/pull/24) ([rocky](https://github.com/rocky))
- Recursive shell call bug [\#23](https://github.com/solvebio/solvebio-python/pull/23) ([rocky](https://github.com/rocky))

## [1.5.1](https://github.com/solvebio/solvebio-python/tree/1.5.1) (2014-09-18)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.5.0...1.5.1)

**Fixed bugs:**

- support partial slice request [\#19](https://github.com/solvebio/solvebio-python/issues/19)

**Closed issues:**

- non-paging Query fetches outside of limit bounds [\#20](https://github.com/solvebio/solvebio-python/issues/20)

**Merged pull requests:**

- Revise not to use omim. Use API key and travis tests. [\#18](https://github.com/solvebio/solvebio-python/pull/18) ([rocky](https://github.com/rocky))
- Minor improvements [\#16](https://github.com/solvebio/solvebio-python/pull/16) ([rocky](https://github.com/rocky))
- Add .netrc login status [\#15](https://github.com/solvebio/solvebio-python/pull/15) ([rocky](https://github.com/rocky))

## [1.5.0](https://github.com/solvebio/solvebio-python/tree/1.5.0) (2014-08-27)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.4.0...1.5.0)

**Closed issues:**

- Test suite & sanity checks [\#2](https://github.com/solvebio/solvebio-python/issues/2)

**Merged pull requests:**

- Add SolveBio API test to SolveBio CLI and add pretty printing for xml fields [\#14](https://github.com/solvebio/solvebio-python/pull/14) ([spaugh](https://github.com/spaugh))

## [1.4.0](https://github.com/solvebio/solvebio-python/tree/1.4.0) (2014-07-24)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.3.4...1.4.0)

**Merged pull requests:**

- Improvements to SolveArgumentParser [\#13](https://github.com/solvebio/solvebio-python/pull/13) ([spaugh](https://github.com/spaugh))

## [1.3.4](https://github.com/solvebio/solvebio-python/tree/1.3.4) (2014-07-17)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.3.3...1.3.4)

**Implemented enhancements:**

- Better explain the sudo password prompt on curl easy install [\#9](https://github.com/solvebio/solvebio-python/issues/9)

**Closed issues:**

- Bulk query interface [\#1](https://github.com/solvebio/solvebio-python/issues/1)

## [1.3.3](https://github.com/solvebio/solvebio-python/tree/1.3.3) (2014-06-12)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.3.2...1.3.3)

## [1.3.2](https://github.com/solvebio/solvebio-python/tree/1.3.2) (2014-06-11)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.3.1...1.3.2)

**Closed issues:**

- Query proxy view for django-solvebio app [\#12](https://github.com/solvebio/solvebio-python/issues/12)

## [1.3.1](https://github.com/solvebio/solvebio-python/tree/1.3.1) (2014-05-28)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.3.0...1.3.1)

## [1.3.0](https://github.com/solvebio/solvebio-python/tree/1.3.0) (2014-05-28)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.2.2...1.3.0)

**Implemented enhancements:**

- Client/API error management and reporting [\#6](https://github.com/solvebio/solvebio-python/issues/6)

**Closed issues:**

- OAuth2 app client\_credentials support [\#10](https://github.com/solvebio/solvebio-python/issues/10)

## [1.2.2](https://github.com/solvebio/solvebio-python/tree/1.2.2) (2014-04-09)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.2.1...1.2.2)

## [1.2.1](https://github.com/solvebio/solvebio-python/tree/1.2.1) (2014-04-08)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.2.0...1.2.1)

**Fixed bugs:**

- Make the netrc path configurable [\#7](https://github.com/solvebio/solvebio-python/issues/7)

## [1.2.0](https://github.com/solvebio/solvebio-python/tree/1.2.0) (2014-04-04)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.1.0...1.2.0)

## [1.1.0](https://github.com/solvebio/solvebio-python/tree/1.1.0) (2014-03-29)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.0.6...1.1.0)

## [1.0.6](https://github.com/solvebio/solvebio-python/tree/1.0.6) (2014-03-28)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.0.5...1.0.6)

## [1.0.5](https://github.com/solvebio/solvebio-python/tree/1.0.5) (2014-03-26)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.0.4...1.0.5)

## [1.0.4](https://github.com/solvebio/solvebio-python/tree/1.0.4) (2014-03-25)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.0.3...1.0.4)

## [1.0.3](https://github.com/solvebio/solvebio-python/tree/1.0.3) (2014-03-20)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.0.2...1.0.3)

## [1.0.2](https://github.com/solvebio/solvebio-python/tree/1.0.2) (2014-03-12)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.0.1...1.0.2)

## [1.0.1](https://github.com/solvebio/solvebio-python/tree/1.0.1) (2014-02-24)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/1.0.0...1.0.1)

## [1.0.0](https://github.com/solvebio/solvebio-python/tree/1.0.0) (2014-02-14)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/0.1.7...1.0.0)

## [0.1.7](https://github.com/solvebio/solvebio-python/tree/0.1.7) (2013-11-01)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/0.1.5...0.1.7)

## [0.1.5](https://github.com/solvebio/solvebio-python/tree/0.1.5) (2013-10-15)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/0.1.4...0.1.5)

## [0.1.4](https://github.com/solvebio/solvebio-python/tree/0.1.4) (2013-10-15)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/0.1.3...0.1.4)

## [0.1.3](https://github.com/solvebio/solvebio-python/tree/0.1.3) (2013-10-14)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/0.1.2...0.1.3)

## [0.1.2](https://github.com/solvebio/solvebio-python/tree/0.1.2) (2013-10-14)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/0.1.1...0.1.2)

## [0.1.1](https://github.com/solvebio/solvebio-python/tree/0.1.1) (2013-10-14)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/0.1.0...0.1.1)

## [0.1.0](https://github.com/solvebio/solvebio-python/tree/0.1.0) (2013-10-14)

[Full Changelog](https://github.com/solvebio/solvebio-python/compare/4d7a467647fd74d7d0638603788f9ff55c9694ac...0.1.0)



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
