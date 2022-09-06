import pyperclip
import json
import math
import time
from PIL import Image, ImageFont, ImageDraw
from datetime import timedelta, datetime
import tkinter as Tk
import tkinter.ttk as ttk
from tkinter import messagebox

class GBFMC():
    def __init__(self):
        self.ver = "1.4"
        print("Granblue Fantasy Match Chart v" + self.ver)
        self.ui = None
        self.data = []
        self.pending = False
        self.font = None
        self.load()

    def load(self):
        try:
            with open('saved.json') as f:
                self.data = json.load(f)
        except:
            pass

    def save(self):
        if self.pending:
            self.pending = False
            try:
                with open('saved.json', 'w') as outfile:
                    json.dump(self.data, outfile)
            except:
                pass

    def getBookmark(self):
        pyperclip.copy("javascript:(function (){let obj = {};let d = new Date();d = (d.getTime() + d.getTimezoneOffset() * 60000);try {if (/^#event\/teamraid[0-9]{3}\/ranking_guild/.test(window.location.hash)) {obj = {timestamp: d - d  % 1200000,you: document.getElementsByClassName(\"txt-total-record\")[0].innerText.replace(/,/g, \"\"),opponent: document.getElementsByClassName(\"txt-total-record\")[4].innerText.replace(/,/g, \"\")}} else if (/^#event\/teamraid[0-9]{3}/.test(window.location.hash)) {obj = {timestamp: d,you: document.getElementsByClassName(\"txt-guild-point\")[0].innerText.replace(/,/g, \"\"),opponent: document.getElementsByClassName(\"txt-rival-point\")[0].innerText.replace(/,/g, \"\")}} else {throw \"Invalid page\"};let copyListener = event => {document.removeEventListener(\"copy\", copyListener, true);event.preventDefault();let clipboardData = event.clipboardData;clipboardData.clearData();clipboardData.setData(\"text/plain\", JSON.stringify(obj))};document.addEventListener(\"copy\", copyListener, true);document.execCommand(\"copy\");} catch(e) {alert(\"No scores found or not a valid page\");}}())")
        if self.ui is not None: self.ui.events.append("The bookmark has been copied")

    def reset(self):
        self.data = []
        self.pending = True
        if self.ui is not None: self.ui.events.append("The match has been reset")

    def addPoint(self):
        try:
            clipboard = json.loads(pyperclip.paste())
            self.data.append([clipboard['timestamp'], int(clipboard['you']), int(clipboard['opponent'])])
            self.pending = True
            if self.ui is not None: self.ui.events.append("The point has been added")
        except:
            if self.ui is not None: self.ui.events.append("Error: Impossible to add the point")

    def jsTimestampToJST(self, t):
        return datetime.fromtimestamp(int(t) // 1000) + timedelta(seconds=32400)

    def drawChart(self, plot, name, filename):
        img = Image.new("RGB", (1300, 850), (255,255,255))
        d = ImageDraw.Draw(img)
        if self.font is None: self.font = ImageFont.truetype("font.ttf", 16)
        
        # settings
        chart_width = 1100
        chart_height = 700
        chart_offset_x = 100
        chart_offset_y = 75
        chart_step_x = 110
        chart_step_y = 175
        
        
        # y grid lines
        for i in range(0, 4):
            d.line([(chart_offset_x, chart_offset_y+chart_step_y*i), (chart_width+chart_offset_x, chart_offset_y+chart_step_y*i)], fill=(200, 200, 200), width=1)
        # x grid lines
        for i in range(0, 10):
            d.line([(chart_offset_x+chart_step_x*i, chart_offset_y), (chart_offset_x+chart_step_x*i, chart_height+chart_offset_y)], fill=(200, 200, 200), width=1)
        # legend
        d.text((10, 10),name,font=self.font,fill=(0,0,0))
        d.line([(150, 15), (170, 15)], fill=(0, 0, 255), width=3)
        d.text((180, 10),"You",font=self.font,fill=(0,0,0))
        d.line([(220, 15), (240, 15)], fill=(255, 0, 0), width=3)
        d.text((250, 10),"Opponent",font=self.font,fill=(0,0,0))
        d.text((chart_width, chart_height+chart_offset_y+40),"Time (JST)",font=self.font,fill=(0,0,0))
        
        # y notes
        miny = 999
        maxy = 0
        for p in plot:
            miny = math.floor(min(miny, p[1], p[2]))
            maxy = math.ceil(max(maxy, p[1], p[2]))
        deltay= maxy - miny
        if deltay <= 0: return None
        tvar = maxy
        for i in range(0, 5):
            d.text((chart_offset_x-60, chart_offset_y-10+chart_step_y*i),"{:.2f}".format(float(tvar)).replace('.00', '').replace('.10', '.1').replace('.20', '.2').replace('.30', '.3').replace('.40', '.4').replace('.50', '.5').replace('.60', '.6').replace('.70', '.7').replace('.80', '.8').replace('.90', '.9').replace('.0', '').rjust(6),font=self.font,fill=(0,0,0))
            tvar -= deltay / 4
        # x notes
        minx = plot[0][0]
        maxx = plot[-1][0]
        deltax = maxx - minx
        deltax = (deltax.seconds + deltax.days * 86400)
        if deltax <= 0: return None
        tvar = minx
        for i in range(0, 11):
            d.text((chart_offset_x-15+chart_step_x*i, chart_height+chart_offset_y+10),"{:02d}:{:02d}".format(tvar.hour, tvar.minute),font=self.font,fill=(0,0,0))
            tvar += timedelta(seconds=deltax/10)

        # lines
        lines = [[], []]
        for p in plot:
            x = p[0] - minx
            x = (x.seconds + x.days * 86400)
            x = chart_offset_x + chart_width * (x / deltax)
            y = maxy - p[1]
            y = chart_offset_y + chart_height * (y / deltay)
            lines[0].append((x, y))
            y = maxy - p[2]
            y = chart_offset_y + chart_height * (y / deltay)
            lines[1].append((x, y))

        # plot lines
        d.line([(chart_offset_x, chart_offset_y), (chart_offset_x, chart_height+chart_offset_y), (chart_offset_x+chart_width, chart_height+chart_offset_y)], fill=(0, 0, 0), width=1)
        d.line(lines[0], fill=(0, 0, 255), width=3, joint="curve")
        d.line(lines[1], fill=(255, 0, 0), width=3, joint="curve")

        img.save(filename, format="PNG")

    def data2speed(self):
        speed_data = []
        for i in range(1, len(self.data)):
            delta = 1000000 * (self.data[i][0] - self.data[i-1][0]) / 60000
            speed_data.append([self.jsTimestampToJST(self.data[i][0]), (self.data[i][1]-self.data[i-1][1]) / delta, (self.data[i][2]-self.data[i-1][2]) / delta])
        return speed_data

    def drawSpeedChart(self):
        plot = self.data2speed()
        if len(plot) < 1: return False
        self.drawChart(plot, "Speed (M/min)", "speed.png")
        return True

    def data2point(self):
        point_data = []
        for i in range(0, len(self.data)):
            point_data.append([self.jsTimestampToJST(self.data[i][0]), self.data[i][1] / 1000000, self.data[i][2] / 1000000])
        return point_data

    def drawPointChart(self):
        plot = self.data2point()
        if len(plot) < 2: return False
        self.drawChart(plot, "Scores (M)", "score.png")
        return True

    def delta2str(self, delta, mode=1):
        match mode:
            case 3: return "{}d{}h{}m{}s".format(delta.days, delta.seconds // 3600, (delta.seconds // 60) % 60, delta.seconds % 60)
            case 2: return "{}d{}h{}m".format(delta.days, delta.seconds // 3600, (delta.seconds // 60) % 60)
            case 1: return "{}h{}m".format(delta.seconds // 3600, (delta.seconds // 60) % 60)
            case _: return "{}m".format(delta.seconds // 60)

    def report(self):
        if len(self.data) < 2: return None
        report = None
        max_speed = [0, 0]
        first_timestamp = self.jsTimestampToJST(self.data[0][0])
        last_timestamp = None
        for i in range(1, len(self.data)):
            delta = 1000000 * (self.data[i][0] - self.data[i-1][0]) / 60000
            max_speed = [max(max_speed[0], (self.data[i][1]-self.data[i-1][1]) / delta), max(max_speed[1], (self.data[i][2]-self.data[i-1][2]) / delta)]
            last_timestamp = self.jsTimestampToJST(self.data[i][0])
        if last_timestamp is not None:
            end_time = last_timestamp.replace(day=last_timestamp.day+1, hour=0, minute=0, second=0, microsecond=0)
            remaining = (end_time - last_timestamp)
            delta = 1000000 * (last_timestamp - first_timestamp).seconds / 60
            avg_speed = [(self.data[-1][1] - self.data[0][1]) / delta, (self.data[-1][2] - self.data[0][2]) / delta]
            report = {}
            report["remaining"] = "Remaining Time: " + self.delta2str(remaining)
            report["lead"] = "Difference: {:,}".format(self.data[-1][1] - self.data[-1][2])
            report["you"] = "Current Score: {:,}\nAverage Speed: {:.2f}M/min\nTop Speed: {:.2f}M/min\nEstimations: {:,} to {:,}".format(self.data[-1][1], avg_speed[0], max_speed[0], math.ceil(self.data[-1][1] + 1000000 * avg_speed[0] * remaining.seconds / 60), math.ceil(self.data[-1][1] + 1000000 * max_speed[0] * remaining.seconds / 60))
            report["opponent"] = "Current Score: {:,}\nAverage Speed: {:.2f}M/min\nTop Speed: {:.2f}M/min\nEstimations: {:,} to {:,}".format(self.data[-1][2], avg_speed[1], max_speed[1], math.ceil(self.data[-1][2] + 1000000 * avg_speed[1] * remaining.seconds / 60), math.ceil(self.data[-1][2] + 1000000 * max_speed[1] * remaining.seconds / 60))
        return report

    def run(self):
        report = self.report()
        if report is None:
            if self.ui is not None: self.ui.events.append("Error: Nothing to report")
        else:
            msg = report["remaining"] + "\n" + report["lead"] + "\n\n" + report["you"] + "\n\n" + report["opponent"]
            with open("report.txt", mode="w", encoding="utf-8") as f:
                f.write(msg)
            msg += "\n"
            if self.drawSpeedChart():
                msg += "\nspeed.png has been saved"
            if self.drawPointChart():
                msg += "\nscore.png has been saved"
            if self.ui is not None: self.ui.events.append(msg)

class Interface(Tk.Tk): # interface
    BW = 30
    BH = 2
    def __init__(self, gbfmc):
        self.gbfmc = gbfmc
        self.gbfmc.ui = self
        self.apprunning = True
        self.events = []
        # window
        Tk.Tk.__init__(self,None)
        self.title("GBFMC")
        self.resizable(width=False, height=False) # not resizable
        self.protocol("WM_DELETE_WINDOW", self.close) # call close() if we close the window
        # main
        Tk.Button(self, text="Bookmark", command=self.gbfmc.getBookmark, height=self.BH, width=self.BW).grid(row=0, column=0, sticky="we")
        Tk.Button(self, text="Reset", command=self.gbfmc.reset, height=self.BH, width=self.BW).grid(row=1, column=0, sticky="we")
        Tk.Button(self, text="Add Point", command=self.gbfmc.addPoint, height=self.BH, width=self.BW).grid(row=2, column=0, sticky="we")
        Tk.Button(self, text="Report", command=self.gbfmc.run, height=self.BH, width=self.BW).grid(row=3, column=0, sticky="we")

    def run(self):
        # main loop
        while self.apprunning:
            if len(self.events) > 0:
                messagebox.showinfo(title="Info", message=self.events[0])
                self.events.pop(0)
            self.update()
            time.sleep(0.03)

    def close(self): # called by the app when closed
        self.apprunning = False
        self.gbfmc.save()
        self.destroy() # destroy the window

if __name__ == "__main__":
    Interface(GBFMC()).run()