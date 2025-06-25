from sys import argv, exit
from os import listdir
from os.path import exists
from PyQt5.QtWidgets import (
    QApplication, QWidget, QListWidget, QLabel, QHBoxLayout, QVBoxLayout,
    QTabWidget, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsRectItem, QToolTip, QListWidgetItem, QSlider, QPushButton
)
from PyQt5.QtGui import QPixmap, QPen, QColor, QPainter
from PyQt5.QtCore import Qt, QRectF, QTimer
from scipy.io import loadmat
from matplotlib.pyplot import subplots
from numpy import (
    pi, vstack, empty_like, array, sin, cos, where, min, max
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT

class HoverRect(QGraphicsRectItem):
    def __init__(self, rect, text):
        super().__init__(rect)
        self.text = text
        self.setPen(QPen(QColor(100, 100, 255, 150), 2, Qt.DashLine))
        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        QToolTip.showText(event.screenPos(), self.text)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        QToolTip.hideText()
        super().hoverLeaveEvent(event)

class LegendItemWidget(QWidget):
    def __init__(self, color, text):
        super().__init__()
        self.color = color
        self.colorLabel = QLabel()
        self.colorLabel.setFixedSize(16, 16)
        self.setColor(color)
        self.textLabel = QLabel(text)
        layout = QHBoxLayout()
        layout.setContentsMargins(2, 0, 2, 0)
        layout.addWidget(self.colorLabel)
        layout.addWidget(self.textLabel)
        layout.addStretch()
        self.setLayout(layout)

    def setColor(self, color):
        self.color = color
        qcolor = QColor()
        if isinstance(color, str):
            qcolor.setNamedColor(color)
        elif isinstance(color, tuple) or isinstance(color, list):
            r = int(color[0]*255)
            g = int(color[1]*255)
            b = int(color[2]*255)
            qcolor.setRgb(r, g, b)
        elif isinstance(color, QColor):
            qcolor = color
        else:
            qcolor = QColor(0,0,0)
        self.colorLabel.setStyleSheet(f"background-color: {qcolor.name()}; border: 1px solid black;")

class DatasetPreview(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dataset Preview")

        self.files = []
        self.parameters = []
        self.file_data = {}

        self.fileList = QListWidget()
        self.fileList.setSelectionMode(QListWidget.MultiSelection)
        self.fileLabel = QLabel("File List")

        self.paramList = QListWidget()
        self.paramList.setSelectionMode(QListWidget.MultiSelection)
        self.paramLabel = QLabel("Parameter List")

        self.figure, self.ax = subplots()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.fileLabel)
        leftLayout.addWidget(self.fileList)

        middleLayout = QVBoxLayout()
        middleLayout.addWidget(self.paramLabel)
        middleLayout.addWidget(self.paramList)
        middleLayout.setContentsMargins(0, 0, 0, 0)

        plotLayout = QVBoxLayout()
        plotLayout.addWidget(self.toolbar)
        plotLayout.addWidget(self.canvas)

        self.legendList = QListWidget()
        self.legendList.setMaximumHeight(150)
        self.legendList.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.legendList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        plotLayout.addWidget(self.legendList)

        previewLayout = QHBoxLayout()
        previewLayout.addLayout(leftLayout, 2)
        previewLayout.addLayout(middleLayout, 1)
        previewLayout.addLayout(plotLayout, 4)

        previewTab = QWidget()
        previewTab.setLayout(previewLayout)

        filterTab = QWidget()
        filterLayout = self.createDetectionAlgorithmLayout()
        filterTab.setLayout(filterLayout)

        dxxTab = QWidget()
        dxxTab.setLayout(self.createPresentationLayout())

        self.tabs = QTabWidget()
        self.tabs.addTab(previewTab, "Visualization")
        self.tabs.addTab(dxxTab, "DXX Help")
        self.tabs.addTab(filterTab, "Detection Algorithm")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.tabs)
        self.setLayout(mainLayout)

        self.loadFiles()

        self.fileList.itemSelectionChanged.connect(self.updateParameters)
        self.paramList.itemSelectionChanged.connect(self.updatePlot)

    def createPresentationLayout(self):
        layout = QVBoxLayout()
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        image_path = 'dxx_positions.png'
        if exists(image_path):
            self.pixmap = QPixmap(image_path)
            self.pixmap_item = QGraphicsPixmapItem(self.pixmap)
            self.scene.addItem(self.pixmap_item)

            self.relative_rects = [
                (0.0225, 0.1050, 0.075, 0.05, "94.9 %"), # D24
                (0.0225, 0.1650, 0.075, 0.05, "92.1 %"), # D23
                (0.2700, 0.1925, 0.075, 0.05, "82.4 %"), # D22
                (0.2700, 0.2525, 0.075, 0.05, "78.6 %"), # D21
                (0.6825, 0.1925, 0.075, 0.05, "74.1 %"), # D20
                (0.0225, 0.2925, 0.075, 0.05, "72.2 %"), # D19
                (0.0225, 0.3525, 0.075, 0.05, "64.8 %"), # D18
                (0.6825, 0.2525, 0.075, 0.05, "62.5 %"), # D17
                (0.2700, 0.3725, 0.075, 0.05, "61.6 %"), # D16
                (0.5825, 0.3725, 0.075, 0.05, "59.7 %"), # D15
                (0.5825, 0.4325, 0.075, 0.05, "52.3 %"), # D14
                (0.2700, 0.4325, 0.075, 0.05, "50.0 %"), # D13
                (0.0225, 0.5525, 0.075, 0.05, "44.9 %"), # D12
                (0.0225, 0.6125, 0.075, 0.05, "42.2 %"), # D11
                (0.2700, 0.6300, 0.075, 0.05, "32.4 %"), # D10
                (0.2700, 0.6900, 0.075, 0.05, "29.6 %"), # D09
                (0.6825, 0.7300, 0.075, 0.05, "25.0 %"), # D08
                (0.0225, 0.7300, 0.075, 0.05, "22.2 %"), # D07
                (0.0225, 0.7900, 0.075, 0.05, "14.8 %"), # D06
                (0.6825, 0.7900, 0.075, 0.05, "12.9 %"), # D05
                (0.2700, 0.8100, 0.075, 0.05, "12.5 %"), # D04
                (0.5825, 0.8100, 0.075, 0.05, "10.0 %"), # D03
                (0.5825, 0.8700, 0.075, 0.05, "2.31 %"), # D02
                (0.2700, 0.8700, 0.075, 0.05, "0.46 %")  # D01
            ]

            self.hover_rects = []
            self.updateHoverRects()

        layout.addWidget(self.view)
        self.view.resizeEvent = self.onViewResize

        return layout

    def updateHoverRects(self):
        for r in self.hover_rects:
            self.scene.removeItem(r)
        self.hover_rects.clear()

        w = self.pixmap.width()
        h = self.pixmap.height()

        for (rel_x, rel_y, rel_w, rel_h, text) in self.relative_rects:
            rect = QRectF(rel_x * w, rel_y * h, rel_w * w, rel_h * h)
            hover_rect = HoverRect(rect, text)
            self.scene.addItem(hover_rect)
            self.hover_rects.append(hover_rect)

    def onViewResize(self, event):
        if hasattr(self, 'pixmap_item'):
            self.view.fitInView(self.pixmap_item, Qt.KeepAspectRatio)
            self.updateHoverRects()
        super(QGraphicsView, self.view).resizeEvent(event)

    def loadFiles(self):
        self.files = [f for f in listdir('.') if f.endswith('.mat')]
        self.fileList.addItems(self.files)

    def updateParameters(self):
        selected_files = [item.text() for item in self.fileList.selectedItems()]
        all_params = set()
        self.file_data.clear()

        for f in selected_files:
            try:
                data = loadmat(f)
                self.file_data[f] = data
                params = [k for k, v in data.items()
                          if (not k.startswith('__') and
                              k != 't' and
                              hasattr(v, 'shape') and
                              (v.dtype.kind in ('f', 'i', 'b', 'u')))]
                all_params.update(params)
            except:
                pass

        self.paramList.clear()
        sorted_params = sorted(all_params)
        self.paramList.addItems(sorted_params)

        self.ax.clear()
        self.ax.set_title("Select parameters to plot")
        self.canvas.draw()

        self.legendList.clear()

    def updatePlot(self):
        selected_files = [item.text() for item in self.fileList.selectedItems()]
        selected_params = [item.text() for item in self.paramList.selectedItems()]

        self.ax.clear()
        self.legendList.clear()

        if not selected_files or not selected_params:
            self.ax.set_title("Select files and parameters")
            self.canvas.draw()
            return

        for f in selected_files:
            data = self.file_data.get(f)
            if data is None:
                continue

            t = data.get('t', None)
            if t is None:
                continue

            for p in selected_params:
                y = data.get(p, None)
                if y is None:
                    continue

                y = y.squeeze()
                t_ = t.squeeze()

                if y.shape != t_.shape:
                    continue

                label = f"{f}: {p}"
                line, = self.ax.plot(t_, y, label=label)

                item = QListWidgetItem()
                self.legendList.addItem(item)
                color = line.get_color()
                widget = LegendItemWidget(color, label)
                self.legendList.setItemWidget(item, widget)
                item.setSizeHint(widget.sizeHint())

        self.ax.set_title("Dataset Visualization") 
        self.canvas.draw()
    
    def createDetectionAlgorithmLayout(self):
        layout = QHBoxLayout()

        self.detectionFileList = QListWidget()
        self.detectionFileList.setSelectionMode(QListWidget.SingleSelection)

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(QLabel("File List"))
        leftLayout.addWidget(self.detectionFileList)

        plotLayout = QVBoxLayout()
        plotLayout.setContentsMargins(0,0,0,0)

        self.fig_detection, self.ax_detection = subplots(3,1,sharex=True, figsize=(6,6))
        self.canvas_detection = FigureCanvas(self.fig_detection)
        self.toolbar_detection = NavigationToolbar2QT(self.canvas_detection, self)

        plotLayout.addWidget(self.toolbar_detection)
        plotLayout.addWidget(self.canvas_detection)

        cometLayout = QVBoxLayout()
        cometLayout.setContentsMargins(0,0,0,0)

        self.fig_comet, self.ax_comet = subplots(figsize=(5,5))
        self.canvas_comet = FigureCanvas(self.fig_comet)
        self.toolbar_comet = NavigationToolbar2QT(self.canvas_comet, self)
        
        cometLayout.addWidget(self.toolbar_comet)
        cometLayout.addWidget(self.canvas_comet)
        
        self.slider_comet = QSlider(Qt.Horizontal)
        self.slider_comet.setMinimum(0)
        self.slider_comet.setMaximum(0)
        self.slider_comet.setValue(0)
        self.slider_comet.setTickPosition(QSlider.TicksBelow)
        self.slider_comet.setTickInterval(1)
        
        self.label_slider = QLabel("time: 0 s")
        self.label_slider.setAlignment(Qt.AlignCenter)

        self.slider_comet.valueChanged.connect(self.updateCometPlot)
        
        self.play_button = QPushButton("Play")
        self.is_playing = False
        self.comet_step = 50 
        self.timer = QTimer()
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.advanceSlider)
        
        def togglePlayPause():
            if self.is_playing:
                self.timer.stop()
                self.play_button.setText("Play")
            else:
                if self.slider_comet.value() >= self.slider_comet.maximum():
                    self.slider_comet.setValue(0)
                self.timer.start()
                self.play_button.setText("Pause")
            self.is_playing = not self.is_playing

        self.play_button.clicked.connect(togglePlayPause)

        slider_control_layout = QHBoxLayout()
        slider_control_layout.addWidget(self.play_button)
        slider_control_layout.addWidget(self.slider_comet)

        cometLayout.addLayout(slider_control_layout)
        cometLayout.addWidget(self.label_slider)
        
        cometLayout.setStretch(0, 0)
        cometLayout.setStretch(1, 15)
        cometLayout.setStretch(2, 1)
        cometLayout.setStretch(3, 0)
        layout.addLayout(leftLayout, 2)
        layout.addLayout(plotLayout, 3)
        layout.addLayout(cometLayout, 3)

        self.detectionFileList.clear()
        files = [f for f in listdir('.') if f.endswith('.mat')]
        self.detectionFileList.addItems(files)

        self.detectionFileList.itemClicked.connect(self.updateDetectionPlots)

        self.anim = None

        return layout

    def updateDetectionPlots(self):
        item = self.detectionFileList.currentItem()
        if item is None:
            return

        filename = item.text()
        try:
            data = loadmat(filename)
        except:
            return

        t = data.get('t', None)
        Theta_Estimado = data.get('Theta_est', None)
        Ifault = data.get('Ifault', None)
        Ia = data.get('Ia', None)
        Ib = data.get('Ib', None)
        Ic = data.get('Ic', None)

        if any(x is None for x in [t, Theta_Estimado, Ifault, Ia, Ib, Ic]):
            return

        time_vector = t.squeeze()
        theta_ele = (2 * Theta_Estimado.squeeze() - pi / 2)

        i_fault = Ifault.squeeze()
        i_a_gen = Ia.squeeze()
        i_b_gen = Ib.squeeze()
        i_c_gen = Ic.squeeze()

        i_abc_gen = vstack((i_a_gen, i_b_gen, i_c_gen))

        def abc2dq0(u, theta):
            y = empty_like(u)
            for i in range(len(theta)):
                P = 2/3 * array([
                    [sin(theta[i]), sin(theta[i] - 2 * pi / 3), sin(theta[i] + 2 * pi / 3)],
                    [cos(theta[i]), cos(theta[i] - 2 * pi / 3), cos(theta[i] + 2 * pi / 3)],
                    [0.5, 0.5, 0.5]
                ])
                y[:, i] = P @ u[:, i]
            return y

        i_dq0neg_gen = abc2dq0(i_abc_gen, -theta_ele)

        sample_f = 20000
        f_cutoff = 15
        Wn = f_cutoff / sample_f
        from scipy.signal import butter, lfilter
        b_filterLP, a_filterLP = butter(3, Wn, 'low')

        i_dq0neg_gen_filterLP = empty_like(i_dq0neg_gen)
        for i in range(3):
            i_dq0neg_gen_filterLP[i, :] = lfilter(b_filterLP, a_filterLP, i_dq0neg_gen[i, :])

        t_ini = 0.5
        t_fin = 2.0

        idx = where((time_vector >= t_ini) & (time_vector <= t_fin))[0]
        
        self.time_slider = time_vector[idx]
        self.slider_comet.setMaximum(len(self.time_slider) - 1)
        self.slider_comet.setValue(len(self.time_slider) - 1)

        self.ax_detection[0].clear()
        self.ax_detection[0].plot(time_vector[idx], i_fault[idx])
        self.ax_detection[0].set_ylabel('$i_{fault}$ (A)')

        self.ax_detection[1].clear()
        self.ax_detection[1].plot(time_vector[idx], i_abc_gen[:, idx].T)
        self.ax_detection[1].set_ylabel('$i_{abc,gen}$ (A)')

        self.ax_detection[2].clear()
        self.ax_detection[2].plot(time_vector[idx], i_dq0neg_gen_filterLP[:2, idx].T)
        self.ax_detection[2].set_ylabel('$i_{dq-,s}$ (A)')
        self.ax_detection[2].set_xlabel('time (s)')

        self.canvas_detection.draw()

        self.ax_comet.clear()
        self.ax_comet.set_xlim(min(i_dq0neg_gen_filterLP[0, idx]), max(i_dq0neg_gen_filterLP[0, idx]))
        self.ax_comet.set_ylim(min(i_dq0neg_gen_filterLP[1, idx]), max(i_dq0neg_gen_filterLP[1, idx]))
        self.ax_comet.set_title('Comet plot')

        xdata = i_dq0neg_gen_filterLP[0, idx]
        ydata = i_dq0neg_gen_filterLP[1, idx]

        self.ax_comet.plot(xdata, ydata, 'b-')
        self.ax_comet.plot(xdata[-1], ydata[-1], 'ro')
        
        self.i_dq0neg_gen_filterLP = i_dq0neg_gen_filterLP
        self.idx = idx

        self.canvas_comet.draw()
        
    def updateCometPlot(self, value):
        if hasattr(self, 'time_slider'):
            t_value = self.time_slider[value]
            self.label_slider.setText(f"time: {t_value:.4f} s")
        else:
            self.label_slider.setText(f"time: {value} s")

        if not hasattr(self, 'i_dq0neg_gen_filterLP') or not hasattr(self, 'idx'):
            return

        idx = self.idx
        data_len = len(idx)

        if value >= data_len:
            value = data_len - 1

        xdata = self.i_dq0neg_gen_filterLP[0, idx]
        ydata = self.i_dq0neg_gen_filterLP[1, idx]

        self.ax_comet.clear()
        self.ax_comet.set_xlim(min(xdata), max(xdata))
        self.ax_comet.set_ylim(min(ydata), max(ydata))
        self.ax_comet.set_title('Comet plot')

        self.ax_comet.plot(xdata[:value+1], ydata[:value+1], 'b-')
        self.ax_comet.plot(xdata[value], ydata[value], 'ro')

        self.canvas_comet.draw()
        
    def advanceSlider(self):
        current_value = self.slider_comet.value()
        next_value = current_value + self.comet_step
        if next_value <= self.slider_comet.maximum():
            self.slider_comet.setValue(next_value)
        else:
            self.slider_comet.setValue(self.slider_comet.maximum())
            self.timer.stop()
            self.play_button.setText("Play")
            self.is_playing = False


if __name__ == "__main__":
    app = QApplication(argv)
    w = DatasetPreview()
    w.show()
    exit(app.exec_())
