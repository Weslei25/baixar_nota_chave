from pynfe.processamento.comunicacao import ComunicacaoSefaz
from pynfe.utils.descompactar import DescompactaGzip
from pynfe.utils.flags import NAMESPACE_NFE
from lxml import etree
from config import *
from PyQt5 import QtWidgets
from tela import Ui_MainWindow


class Tela(QtWidgets.QMainWindow):# Classe que inicializa o sistema
    
    def __init__(self, *args, **argvs):# Metodo construtor da aplicação
        super(Tela, self).__init__(*args, **argvs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self._get_pegar_dados)
        self.ui.pushButton_2.clicked.connect(self._get_chaves)
        self.ui.pushButton_3.clicked.connect(self._get_certificado)


    def _get_pegar_dados(self):
        pass
        chaves=self.ui.lineEdit.text()
        certificado=self.ui.lineEdit_2.text()
        senha=self.ui.lineEdit_3.text()
        CNPJ=self.ui.lineEdit_4.text()
        uf=self.ui.lineEdit_5.text()
        
        homologacao=False
        ultNSU=0
        cStat=0
        maxNSU=0
        NSU=0

        self._set_baixar_notas(chaves=chaves, certificado=certificado, senha=senha, uf=uf, CNPJ=CNPJ)

    def _get_certificado(self):
        try:
            
            salvar = QtWidgets.QFileDialog.getOpenFileName()[0]
            
            if not '.pfx' in salvar:
                QtWidgets.QMessageBox.warning(
                    self, 'Atenção', 'Certificado invalido \n{}'.format(salvar))
                return
            self.ui.lineEdit_4.setText(salvar)
        except Exception as erro:
            QtWidgets.QMessageBox.information(self, 'Erro', '{}'.format(erro))
            return

    def _get_chaves(self):
        try:
            
            salvar = QtWidgets.QFileDialog.getOpenFileName()[0]
            
            if not '.txt' in salvar:
                QtWidgets.QMessageBox.information(
                    self, 'Atenção', 'Somente arquivos de texto *.TXT \n{}'.format(salvar))
                return
            self.ui.lineEdit_4.setText(salvar)
        except Exception as erro:
            QtWidgets.QMessageBox.warning(self, 'Erro', '{}'.format(erro))
            return

    def _set_baixar_notas(self, chaves=None, certificado=None, senha=None, uf=None, homologacao=False, CNPJ=None, ultNSU=0, cStat=0, maxNSU=0, NSU=0):

        try:
                    
            with open(chaves, 'r') as files:
                for chave in files:
                    CHAVE = chave[0:44]

                
                    con = ComunicacaoSefaz(uf, certificado, senha, homologacao)
                    xml = con.consulta_distribuicao(cnpj=CNPJ, chave=CHAVE)
                    NSU = str(NSU).zfill(15)
                    print(f'Nova consulta a partir do NSU: {NSU}')
                    logging.info(f'Nova consulta a partir do NSU: {NSU}')
                    with open(f'./xml/consulta_distrib_gzip-{NSU}.xml', 'w+') as f:
                        f.write(xml.text)

                    #resposta = etree.fromstring(xml.content)
                    #print(resposta)
                    resposta = etree.parse(f'./xml/consulta_distrib_gzip-{NSU}.xml')
                    ns = {'ns': NAMESPACE_NFE}
                    
                    contador_resposta = len(resposta.xpath('//ns:retDistDFeInt/ns:loteDistDFeInt/ns:docZip', namespaces=ns))
                    print(f'Quantidade de NSUs na consulta atual: {contador_resposta}')
                    logging.info(f'Quantidade de NSUs na consulta atual: {contador_resposta}')

                    cStat = resposta.xpath('//ns:retDistDFeInt/ns:cStat', namespaces=ns)[0].text
                    print(f'cStat: {cStat}')
                    logging.info(f'cStat: {cStat}')

                    xMotivo = resposta.xpath('//ns:retDistDFeInt/ns:xMotivo', namespaces=ns)[0].text
                    print(f'xMotivo: {xMotivo}')    
                    logging.info(f'xMotivo: {xMotivo}')

                    #maxNSU = resposta.xpath('//ns:retDistDFeInt/ns:maxNSU', namespaces=ns)[0].text
                    print(f'maxNSU: {maxNSU}')
                    logging.info(f'maxNSU: {maxNSU}')

                    # 137=nao tem mais arquivos e 138=existem mais arquivos para baixar
                    if (cStat == '138'):
                        for contador_xml in range(contador_resposta):
                            tipo_schema = resposta.xpath('//ns:retDistDFeInt/ns:loteDistDFeInt/ns:docZip/@schema', namespaces=ns)[contador_xml]
                            numero_nsu = resposta.xpath('//ns:retDistDFeInt/ns:loteDistDFeInt/ns:docZip/@NSU', namespaces=ns)[contador_xml]
                            
                            #nfe = 'procNFe_v4.00.xsd'
                            #evento = 'procEventoNFe_v1.00.xsd'
                            #resumo = 'resNFe_v1.01.xsd'
                            if (tipo_schema == 'procNFe_v4.00.xsd'):#  or (tipo_schema == 'resNFe_v1.01.xsd'): 
                                zip_resposta = resposta.xpath('//ns:retDistDFeInt/ns:loteDistDFeInt/ns:docZip', namespaces=ns)[contador_xml].text
                                
                                descompactar_resposta = DescompactaGzip.descompacta(zip_resposta)
                                texto_descompactado = etree.tostring(descompactar_resposta).decode('utf-8')
                                caminho_arquivo = f'./xml/{CHAVE}.xml'
                                with open(caminho_arquivo, 'w+', encoding='UTF-8') as f:
                                    f.write(texto_descompactado)

                        # NSU = resposta.xpath('//ns:retDistDFeInt/ns:ultNSU', namespaces=ns)[0].text
                        print(f'NSU: {NSU}')
                        logging.info(f'NSU: {NSU}')
                        continue

                    elif (cStat == '137'):
                        print(f'Não há mais documentos a pesquisar')
                        logging.warning(f'Não há mais documentos a pesquisar')
                        continue
                        break
                    else:
                        print(f'Falha')
                        logging.error(f'Falha')
                        continue
                        #break
        except Exception as erro:
            logging.exception(erro)
            QtWidgets.QMessageBox.critical(self, "Atenção", "{}\nVerifique os logs".format(erro))
            return
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('fusion')
    tela = Tela()
    tela.show()
    sys.exit(app.exec_())