# Maintainer: Louis Kleiver louis.kleiver@gmail.com
pkgname=eiota
pkgver=1.0.0
pkgrel=0
pkgdesc="A simple python script to simplify BLIH usage for Epitech students."
arch=('any')
url="https://github.com/mrCaelum/eiota"
license=('MIT')
depends=('python>=3.3.0'
	'python-requests'
	'git'
    'blih')
source=("${pkgname}-${pkgver}.tar.gz::https://github.com/mrCaelum/${pkgname}/releases/download/v${pkgver}/v${pkgver}.tar.gz")
sha256sums=('SKIP')

prepare() {
	sed -i s/python3.3/python/ "${pkgname}/${pkgname}.py"
}

build() {
    cd "${pkgname}"
	mv "${pkgname}.py" "${pkgname}"
	chmod 755 "${pkgname}"
}

package() {
	mkdir -p "${pkgdir}/usr/bin"
	cp -a "${pkgname}/blih" "${pkgdir}/usr/bin"
}