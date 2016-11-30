%{?scl:%scl_package freemarker}
%{!?scl:%global pkg_name %{name}}
%{?java_common_find_provides_and_requires}

%global baserelease 2

# Prevent brp-java-repack-jars from being run.
%global __jar_repack %{nil}

%global checkForbiddenJARFiles F=`find -type f -iname '*.jar'`; [ ! -z "$F" ] && \
echo "ERROR: Sources should not contain JAR files:" && echo "$F" && exit 1

%global fm_compatible_ver 2.3
%global fm_ver %{fm_compatible_ver}.23

Name:           %{?scl_prefix}freemarker
Version:        %{fm_ver}
Release:        2.%{baserelease}%{?dist}
Summary:        A template engine
License:        BSD
URL:            http://freemarker.sourceforge.net/
Source0:        http://downloads.sourceforge.net/%{pkg_name}/%{pkg_name}-%{version}.tar.gz
Source1:        pom.xml

# Remove JSP 1.x and 2.0 API usage
Patch1:         jsp-api.patch
# Compile only the classes compatible with the version of jython
Patch2:         jython-compatibility.patch
# illegal character in the javadoc comment
Patch3:         fix-javadoc-encoding.patch
# Fix ivy configuration
Patch4:         ivy-configuration.patch
# Disable JavaRebelIntegration
Patch5:         no-javarebel.patch
# enable jdom extension
Patch6:         enable-jdom.patch
# use system javacc and fix Token.java
Patch7:         javacc.patch

BuildArch:      noarch

BuildRequires: %{?scl_prefix_maven}maven-local
BuildRequires: %{?scl_prefix_maven}javacc-maven-plugin
BuildRequires: %{?scl_prefix_java_common}apache-commons-logging
BuildRequires: %{?scl_prefix_maven}aqute-bnd
BuildRequires: %{?scl_prefix_maven}avalon-logkit >= 1.2
BuildRequires: %{?scl_prefix_java_common}log4j >= 1.2
BuildRequires: %{?scl_prefix_maven}sonatype-oss-parent
BuildRequires: %{?scl_prefix_java_common}slf4j-api

%description
FreeMarker is a Java tool to generate text output based on templates.
It is designed to be practical as a template engine to generate web
pages and particularly for servlet-based page production that follows
the MVC (Model View Controller) pattern. That is, you can separate the
work of Java programmers and website designers - Java programmers
needn't know how to design nice websites, and website designers needn't
know Java programming.

%package javadoc
Summary:        Javadoc for %{pkg_name}

%description javadoc
This package contains the API documentation for %{pkg_name}.

%prep
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%setup -q -n %{pkg_name}-%{version} -c

cp -p %{SOURCE1} source/.

find . -name "*.jar" -delete
find . -name "*.class" -delete
rm -rf documentation/_html/api/

%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1

%{__rm} -rf source/ivysettings.xml

# %%{__rm} -rf src/freemarker/core/ParseException.java
%{__rm} -rf source/src/freemarker/core/FMParser.java
%{__rm} -rf source/src/freemarker/core/FMParserConstants.java
%{__rm} -rf source/src/freemarker/core/FMParserTokenManager.java
%{__rm} -rf source/src/freemarker/core/SimpleCharStream.java
%{__rm} -rf source/src/freemarker/core/Token.java
%{__rm} -rf source/src/freemarker/core/TokenMgrError.java
%{?scl:EOF}


%checkForbiddenJARFiles
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x

%mvn_file org.%{pkg_name}:%{pkg_name} %{pkg_name}
%{?scl:EOF}


%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
cd source
%mvn_build -f
sed -i -e 's/build\/classes/target\/classes/' -e '/^Import-Package:/d' osgi.bnd
echo "Import-Package: !freemarker.*,!org.slf4j*,!org.apache.log,!org.apache.log4j,!org.apache.commons.logging,*;resolution:=\"optional\"" >> osgi.bnd
java -DversionForOSGi=%{version} -DversionForMf=%{version} -DmoduleOrg=org.freemarker -DmoduleName=freemarker \
  -jar $(build-classpath aqute-bnd) wrap -properties osgi.bnd target/freemarker-%{version}.jar
mv freemarker-%{version}.bar target/freemarker-%{version}.jar
%{?scl:EOF}


%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
cd source
%mvn_install
cp .mfiles* ..
%{?scl:EOF}


%files -f .mfiles
%doc README.txt
%doc LICENSE.txt NOTICE.txt

%files javadoc -f .mfiles-javadoc
%doc LICENSE.txt NOTICE.txt

%changelog
* Fri Jul 29 2016 Mat Booth <mat.booth@redhat.com> - 2.3.23-2.2
- Build without any optional modules

* Fri Jul 29 2016 Mat Booth <mat.booth@redhat.com> - 2.3.23-2.1
- Auto SCL-ise package for rh-eclipse46 collection

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.3.23-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jan 06 2016 Omair Majid <omajid@redhat.com> - 2.3.23-1
- Update to 2.3.23

* Thu Jul 02 2015 gil cattaneo <puntogil@libero.it> 2.3.19-11
- fix FTBFS
- adapt to current guideline
- fix some rpmlint problems
- enable javadoc task
- enable maven-upload task for generate pom file
- Fix paths to jython

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3.19-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jun 09 2014 Omair Majid <omajid@redhat.com> - 2.3.19-9
- Use .mfiles to pick up xmvn metadata
- Don't use obsolete _mavendepmapfragdir macro
- Fix FTBFS issues

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3.19-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Feb 24 2014 Omair Majid <omajid@redhat.com> - 2.3.19-8
- Require java-headless

* Fri Oct 04 2013 Omair Majid <omajid@redhat.com> - 2.3.19-7
- Fix upstream Source URL for pom file

* Mon Aug 05 2013 Omair Majid <omajid@redhat.com> - 2.3.19-7
- Fix build dependencies

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3.19-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3.19-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Aug 01 2012 Omair Majid <omajid@redhat.com> - 2.3.19-4
- Build remaining classes with target 6 too.
- Fixes RHBZ#842594

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3.19-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jun 27 2012 Omair Majid <omajid@redhat.com> - 2.3.19-2
- Remove obsolete patches

* Tue Jun 05 2012 gil cattaneo <puntogil@libero.it - 2.3.19-2
- update patch for logging

* Thu May 31 2012 Omair Majid <omajid@redhat.com> - 2.3.19-1
- Add dependency on apache-commons-logging

* Wed May 16 2012 gil cattaneo <puntogil@libero.it> - 2.3.19-1
- update to 2.3.19

* Wed Feb 01 2012 Marek Goldmann <mgoldman@redhat.com> - 2.3.13-14
- Added Maven POM, RHBZ#786383

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3.13-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Mar 16 2011 Omair Majid <omajid@redhat.com> - 2.3.13-12
- Drop build dependency on struts
- Remove buildroot cleaning and definition
- Remove versioned jars
- Remove dependency of javadoc subpackage on main package

* Mon Feb 28 2011 Omair Majid <omajid@redhat.com> - 2.3.13-12
- Remove dependency on tomcat5

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3.13-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Sep 13 2010 Alexander Kurtakov <akurtako@redhat.com> 2.3.13-10
- Adapt to tomcat6-el jar rename.

* Mon Sep 13 2010 Alexander Kurtakov <akurtako@redhat.com> 2.3.13-9
- Add tomcat6-libs BR.
- Use global instead of define.

* Sat Feb 27 2010 Victor G. Vasilyev <victor.vasilyev@sun.com> 2.3.13-8
- fix build patch for use of the javacc 5.0
- patch for encoding
- disable brp-java-repack-jars

* Sat Feb 27 2010 Victor G. Vasilyev <victor.vasilyev@sun.com> 2.3.13-7
- patch for logging
- remove name from the summary

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3.13-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3.13-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Sep 01 2008 Victor G. Vasilyev <victor.vasilyev@sun.com> 2.3.13-4
- Redundant dependency upon xerces-j2 is removed (#456276#c6)
- The dos2unix package is added as the build requirements
- The ant-nodeps build-time requirement is added

* Wed Aug 20 2008 Victor G. Vasilyev <victor.vasilyev@sun.com> 2.3.13-3
- The downloads.sourceforge.net host is used in the source URL
- %%{__install} and %%{__cp} are used everywhere
- %%defattr(-,root,root,-) is used everywhere

* Thu Aug 14 2008 Victor G. Vasilyev <victor.vasilyev@sun.com> 2.3.13-2
- Appropriate values of Group Tags are chosen from the official list
- Versions of java-devel & jpackage-utils are corrected
- Name of dir for javadoc is changed
- Manual is removed due to http://freemarker.org/docs/index.html

* Fri Jun 06 2008 Victor G. Vasilyev <victor.vasilyev@sun.com> 2.3.13-1
- Initial version
