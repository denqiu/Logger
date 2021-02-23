from pySql import *
from pyqt5Custom import *

class Action(ChildButton):
    def __init__(self, action, toolTip = None):
        ChildButton.__init__(self)
        self.setObjectName(action)
        border = self.getText("border")["border"]
        if toolTip is None:
            toolTip = action.capitalize()
        border.setToolTip(toolTip)
        self.addText(border)
        self.addTextToGrid("border")
        self.setFixedWidth(30)
        self.currentColor = self.defaultColor()
        
    def defaultColor(self):
        return self.backgroundColor if self.entered else self.hoverColor
                
    def findPoint(self, x, p1, p2):
        slope = (p2.y()-p1.y()) / (p2.x()-p1.x())
        intercept = p1.y()-slope*p1.x()
        return QPoint(x, slope*x + intercept)
    
    def paint(self, p):  
        return p  
    
    def paintEvent(self, event):
        p = QPainter()
        p.begin(self)
        self.currentColor = self.defaultColor()
        p.setPen(QPen(self.currentColor, 2, Qt.SolidLine))
        p = self.paint(p)
        p.end()
        
class Refresh(Action):
    def __init__(self):
        Action.__init__(self, "refresh")
        border = self.getText("border")["border"]
        s = Style(border.styleSheet())
        s.setAttribute("border", "0")
        border.setStyleSheet(s.css())
        self.addText(border)
        self.addTextToGrid("border")
        self.setFixedHeight(30)
        self.setUsersForm(None)
        self.setObjectName("refresh")
        
    def paint(self, p):
        w, h = (self.width(), self.height())
        i = 14
        start = i//2
        s = start//2
        p.drawArc(start, start, w-i, h-i, 30*16, 300*16)
        a = QPoint(w-i, h-i-s)
        b = QPoint(w-i+start+s, start)
        c = self.findPoint(b.x()-2, a, b)
        c.setY(c.y()+start)
        p.setBrush(self.currentColor)
        p.drawPolygon(QPolygon([a, b, c]))
        return p
    
    def mouseLeftReleased(self, QMouseEvent):
        Action.mouseLeftReleased(self, QMouseEvent)
        if self.checkUsersForm():
            print("hi refresh")
#             items = self.__usersForm.getItems()
#             items.clearForm()
#             items.newRow()
#     
    def checkUsersForm(self):
        return not self.__usersForm is None
    
    def setUsersForm(self, usersForm):
        self.__usersForm = usersForm

class Leader(Action):
    def __init__(self, userId):
        self.setLeader(False)
        Action.__init__(self, "leader", "Set leader")
        self.__userId = userId
        self.setUsersFormScroll(None, None)
        
    def paint(self, p):
        i, j, k = (18, 5, 2)
        w, h = (self.width()-i, self.height()-i)
        p.drawEllipse(9, j, w, h)
        start = QPoint(j+k, i)
        w += j
        h -= k
        p.drawArc(start.x(), start.y(), w, h, 0*16, 180*16)
        start.setY(start.y()+h-j+1)
        end = QPoint(start.x()+w, start.y())
        p.drawLine(start, end)
        return p
    
    def defaultColor(self):
        if self.isLeader():
            return self.backgroundColor
        return Action.defaultColor(self)
    
    def paintEvent(self, event):
        Action.paintEvent(self, event)
        if self.isLeader():
            self.setColor(self, self.backgroundRole(), self.hoverColor)
        border = self.getText("border")["border"]
        s = Style(border.styleSheet())
        s.setAttribute("border", "1px solid black")
        border.setStyleSheet(s.css())
        self.addText(border)
        self.addTextToGrid("border")
    
    def getCurrentLeaderId(self):
        return self.__usersForm.getCurrentLeaderId()
    
    def checkLeaderId(self):
        return self.__userId == self.getCurrentLeaderId()
    
    def setLeader(self, isLeader):
        self.__isLeader = isLeader
        
    def isLeader(self):
        return self.__isLeader
    
    def getUserId(self):
        return self.__userId
       
    def mouseLeftReleased(self, QMouseEvent):
        Action.mouseLeftReleased(self, QMouseEvent)
        if not self.isLeader():
            self.setLeader(True)
            self.__usersForm.setCurrentLeader(self.__userId)
            self.__usersForm.setCurrentLeaderButton(self)
        
    def mouseMove(self, QMouseEvent):
        if self.checkUsersScroll():
            self.__usersScroll.setScrollDragged(False)
            self.__usersScroll.mouseMoveEvent(QMouseEvent)
        
    def mouseMiddlePressed(self, QMouseEvent):
        if self.checkUsersScroll():
            self.__usersScroll.mouseMiddlePressed(QMouseEvent)
            
    def mouseMiddleReleased(self, QMouseEvent):
        if self.checkUsersScroll():
            self.__usersScroll.mouseMiddleReleased(QMouseEvent)
            
    def checkUsersForm(self):
        return not self.__usersForm is None
    
    def checkUsersScroll(self):
        return not self.__usersScroll is None
    
    def setUsersFormScroll(self, usersForm, usersScroll):
        self.__usersForm = usersForm
        self.__usersScroll = usersScroll
        if self.checkUsersForm():
            if self.checkLeaderId():
                self.setLeader(True)
                self.__usersForm.setCurrentLeaderButton(self)
    
class Edit(Action):
    def __init__(self, user, userId):
        self.setClicked(False)
        self.setLeader(None)
        self.__userId = userId
        self.__user = user
        self.setUsersFormScroll(None, None)
        Action.__init__(self, "edit")
        
    def setClicked(self, isClicked):
        self.__isClicked = isClicked
        
    def setLeader(self, leader):
        self.__leader = leader
        
    def paint(self, p):
        h, w = (8, self.width())
        p.drawLine(4, h, w-18, h)
        p.drawLine(w-4, h, w-6, h)
        h += 8
        p.drawLine(4, h, w-23, h)
        p.drawLine(w-4, h, w-5, h)
        h += 8
        p.drawLine(4, h, w-24, h)
        p.drawLine(w-4, h, w-10, h)
        a = QPoint(w-12, 4)
        b = QPoint(10, h-8)
        i = 7
        c = QPoint(b.x(), b.y()+i+3)
        d = QPoint(b.x()+i, b.y()+i)
        e = QPoint(a.x()+i, a.y()+i)
        p.drawPolygon(QPolygon([a, b, c, d, e]))
        p.drawLine(b, d)
        i = 3
        f = self.findPoint(a.x()-i, a, b)
        g = self.findPoint(e.x()-i, e, d)
        p.drawLine(f, g)
        return p
    
    def __switchColors(self):
        b = self.backgroundColor
        self.backgroundColor = self.hoverColor
        self.hoverColor = b
    
    def paintEvent(self, event):
        Action.paintEvent(self, event)
        if self.__isClicked:
            self.setClicked(False)
            self.setColor(self, self.backgroundRole(), self.hoverColor)
            self.__switchColors()
            self.__usersForm.setEditorView(self.__user, self.__userId)
            self.__leader.setEnabled(not self.__leader.isEnabled())
        border = self.getText("border")["border"]
        s = Style(border.styleSheet())
        s.setAttribute("border", "1px solid black")
        border.setStyleSheet(s.css())
        self.addText(border)
        self.addTextToGrid("border")
       
    def mouseLeftPressed(self, QMouseEvent):
        Action.mouseLeftPressed(self, QMouseEvent)
        self.setClicked(True)
        
    def mouseMove(self, QMouseEvent):
        if self.checkUsersScroll():
            self.__usersScroll.setScrollDragged(False)
            self.__usersScroll.mouseMoveEvent(QMouseEvent)
        
    def mouseMiddlePressed(self, QMouseEvent):
        if self.checkUsersScroll():
            self.__usersScroll.mouseMiddlePressed(QMouseEvent)
            
    def mouseMiddleReleased(self, QMouseEvent):
        if self.checkUsersScroll():
            self.__usersScroll.mouseMiddleReleased(QMouseEvent)
            
    def getLastEditorId(self):
        return self.__usersForm.getLastEditorId()
    
    def checkEditorId(self):
        return self.__userId == self.getLastEditorId()
    
    def checkUsersForm(self):
        return not self.__usersForm is None
    
    def checkUsersScroll(self):
        return not self.__usersScroll is None
    
    def setUsersFormScroll(self, usersForm, usersScroll):
        self.__usersForm = usersForm
        self.__usersScroll = usersScroll
        if self.checkUsersForm():
            if self.checkEditorId():
                self.setClicked(True)
                
class User(Button):        
    def __init__(self, name, userId):
        self.__usersScroll = None
        user = ButtonText(name, name)
        user.textClickColor = None
        user.textHoverColor = None
        space = ButtonText(attribute="space")
        Button.__init__(self, user, space)
        self.setObjectName(name)
        leader, edit = (Leader(userId), Edit(name, userId))
        self.addChildButtons(leader, edit)
        leader.setButton(None)
        edit.setButton(None)
        boxLayout = BoxLayout(BoxLayout.ALIGN_HORIZONTAL, name, "space", leader.objectName(), edit.objectName())
        self.addBoxLayoutToGrid(boxLayout, Qt.AlignCenter)
        self.clickColor = None
        self.hoverColor = None
        self.setMaximumHeight(30) 
        
    def setUsersFormScroll(self, usersForm, usersScroll):
        self.__usersScroll = usersScroll
        leader, edit = tuple(self.getChildButtons().values())
        leader.setUsersFormScroll(usersForm, usersScroll)
        edit.setUsersFormScroll(usersForm, usersScroll)
        edit.setLeader(leader)
        
    def checkUsersScroll(self):
        return not self.__usersScroll is None
        
    def mouseMove(self, QMouseEvent):
        if self.checkUsersScroll():
            self.__usersScroll.setScrollDragged(False)
            self.__usersScroll.mouseMoveEvent(QMouseEvent)
        
    def mouseMiddlePressed(self, QMouseEvent):
        if self.checkUsersScroll():
            self.__usersScroll.mouseMiddlePressed(QMouseEvent)
            
    def mouseMiddleReleased(self, QMouseEvent):
        if self.checkUsersScroll():
            self.__usersScroll.mouseMiddleReleased(QMouseEvent)
            
class Header(Button):
    def __init__(self, user, userId):
        self.setUsersScroll(None)
        headers = ("Start Date", "End Date", "Description", "Time Spent")
        headers = [" {} ".format(h) for h in headers]
        attributes = ["{} {}".format(h.lower().replace(" ", "_"), userId) for h in headers]
        headerTexts = []
        headers = tuple(zip(headers, attributes))
        for (header, attribute) in headers:
            h = ButtonText(header, attribute, "1px solid black")
            h.setAlignment(Qt.AlignCenter)
            h.textClickColor = None
            h.textHoverColor = None
            headerTexts.append(h)
        Button.__init__(self, *headerTexts)
        self.setObjectName("{}_header".format(user))
        boxLayout = BoxLayout(BoxLayout.ALIGN_HORIZONTAL, *attributes)
        self.addBoxLayoutToGrid(boxLayout)
        self.clickColor = None
        self.hoverColor = None
        self.setMaximumHeight(30)
        
    def setUsersScroll(self, usersScroll):
        self.__usersScroll = usersScroll
        
    def checkUsersScroll(self):
        return not self.__usersScroll is None
        
    def mouseMove(self, QMouseEvent):
        if self.checkUsersScroll():
            self.__usersScroll.setScrollDragged(False)
            self.__usersScroll.mouseMoveEvent(QMouseEvent)
        
    def mouseMiddlePressed(self, QMouseEvent):
        if self.checkUsersScroll():
            self.__usersScroll.mouseMiddlePressed(QMouseEvent)
            
    def mouseMiddleReleased(self, QMouseEvent):
        if self.checkUsersScroll():
            self.__usersScroll.mouseMiddleReleased(QMouseEvent)
            
# class Users(QHBoxLayout):         
#     def __init__(self, logger):
#         QHBoxLayout.__init__(self)
#         logger.db.query("select get_user(user_id) as user, user_id from user order by user_id")
#         users = logger.db.results[2]
#         users = dict([tuple(user.values()) for user in users])
#         self.userIds = users
#         self.users = {}
#         self.items = {}
#         for user in users:
#             userBox = QVBoxLayout()
#             u = Form()
#             button = User(user, logger)
#             button.setFont(logger.getFont(16))
#             if users[user] > 1:
#                 border = button.getText("border")[0]
#                 s = Style(border.styleSheet())
#                 s.setAttribute("border-left", "0")
#                 border.setStyleSheet(s.css())
#                 button.addText(border)
#                 button.addTextToGrid("border")
#             u.addButton(button).addRow()
#             self.users[user] = u
#             userBox.addLayout(u.layout())
#             items = Form()
#             items.isAddingItems(True)
#             items.setRowSize(3)
#             self.items[user] = items
#             userBox.addWidget(ScrollArea(items.group()))
#             self.addLayout(userBox)
#         self.setSpacing(0)

class Items(Form):
    def __init__(self, logger):
        Form.__init__(self, logger)
        self.isAddingItems(True)
        self.setRowSize(4)
    
class Users(Form):
    def __init__(self, logger, deliverable):
        Form.__init__(self, logger)
        search = SearchForm().searchNames("deliverable", "refresh")
        deliverable = deliverable.searchObjects(search).mergeResults().results
        deliverable, refresh = tuple(deliverable.values())
        self.__deliverable = deliverable
        self.__refresh = refresh
        self.tablelize(True)
        logger.db.query("select get_user(user_id) as user, user_id from user order by user_id")
        users = logger.db.results[2]
        users = dict([tuple(user.values()) for user in users])
        for u in users:
            self.addButton(User(u, users[u]), self.getFont(16))
        self.addRow()
        for u in users:
            self.addButton(Header(u, users[u]), self.getFont(14))
        self.addRow()        
        boxLayout = BoxLayout(BoxLayout.ALIGN_VERTICAL, ScrollArea(Items(logger).group()))
        self.addBoxLayout(boxLayout).addRow()

    def getScroll(self):
        search = SearchForm().searchClasses(BoxLayout)
        boxLayout = self.searchObjects(search).mergeResults().results
        boxLayout = tuple(boxLayout.values())[0]
        return boxLayout.getItems()[0]
    
    def getItems(self):
        return self.getScroll().widget().getForm()
    
    def getUsersScroll(self):
        return self.layout().parent().parent().parent()
        
    def setEditorView(self, user, userId):
        search = SearchForm().searchClasses(Button)
        buttons = self.searchObjects(search).mergeResults().results
        buttons = tuple(buttons.values())
        buttons = [b for b in buttons if not user in b.objectName()]
        if self.__currentLeader.getUserId() != userId:
            if self.__currentLeader.isLeader():
                self.__leaveLeader()
            else:
                self.__currentLeader.setLeader(True)
        for b in buttons:
            b.setVisible(not b.isVisible())
        self.updateCurrentEditor(userId)
        self.__refresh.mouseLeftReleased(QMouseEvent)
        self.__refresh.leave(QMouseEvent)
        
    def setCurrentLeaderButton(self, leader):
        self.__currentLeader = leader
        logger = self.getParent()
        logger.db.query("select deliverable_id, deliverable from deliverable where user_id = get_current_leader_id()")
        d = logger.db.results[2][0]
        num, d = tuple(d.values())
        self.__deliverable.setText("Deliverable #{}: {}".format(num, d))
        
    def __leaveLeader(self):
        self.__currentLeader.setLeader(False)
        self.__currentLeader.leave(QMouseEvent)
        
    def setCurrentLeader(self, userId):
        self.__leaveLeader()
        self.updateCurrentLeader(userId)
    
    def getCurrentLeaderId(self):
        return self.getParent().getCurrentLeaderId()
  
    def getCurrentEditorId(self):
        return self.getParent().getCurrentEditorId()
  
    def getLastEditorId(self):
        return self.getParent().getLastEditorId()
  
    def updateCurrentLeader(self, userId):
        return self.getParent().updateCurrentLeader(userId)
        
    def updateCurrentEditor(self, userId):
        return self.getParent().updateCurrentEditor(userId)
        
    def updateLastEditor(self):
        return self.getParent().updateLastEditor()
        
class UsersScroll(ScrollArea):
    def __init__(self, users, logger):
        self.__logger = logger
        ScrollArea.__init__(self, users.group())
        self.setDraggable(True)
        self.setScrollBarVisibility(False, ScrollArea.HORIZONTAL_SCROLLBAR)
    
    def calculateScrollValue(self, bar, currentPosition, startPosition):
        value, _ = ScrollArea.calculateScrollValue(self, bar, currentPosition, startPosition)
        self.__logger.updateHorizontalScroll(value)
        return value
    
    def setHorizontalScrollValue(self):
        self.scrollBarValues[ScrollArea.HORIZONTAL_SCROLLBAR] = self.__logger.getHorizontalScrollValue()
    
    def checkEditorId(self):
        editorId = self.__logger.getCurrentEditorId()
        if editorId is None:
            return False
        return editorId < 1
    
    def mouseMoveEvent(self, QMouseEvent):
        if self.checkEditorId():
            ScrollArea.mouseMoveEvent(self, QMouseEvent)
            
    def mousePressEvent(self, QMouseEvent):
        if self.checkEditorId():
            ScrollArea.mousePressEvent(self, QMouseEvent)
            
    def mouseReleaseEvent(self, QMouseEvent):
        if self.checkEditorId():
            ScrollArea.mouseReleaseEvent(self, QMouseEvent)
        
    def eventFilter(self, QObject, QEvent):
        self.horizontalScrollBar().setValue(self.scrollBarValues[ScrollArea.HORIZONTAL_SCROLLBAR])
        return ScrollArea.eventFilter(self, QObject, QEvent)
        
class Deliverable(Form):
    def __init__(self, logger):
        Form.__init__(self, logger)
        self.addButtonText("", "deliverable", font = self.getFont(18)).addRow(Qt.AlignCenter)
        self.addButton(Refresh()).addRow(Qt.AlignCenter)
    
class Logger(ParentWindow):    
    def __init__(self):
        app = QApplication(sys.argv)
        try:
            self.db = AccessSql(True, accessType=AccessSql.SSH_ACCESS)
            self.__start = True
        except SystemExit as e:
            self.db = e
        super().__init__()
        sys.exit(app.exec_())  
        
    def checkDb(self):
        return not type(self.db) is str
      
    def setupWindow(self):
        ParentWindow.setupWindow(self)
        self.setWindowTitle("CSC 450 Music Sharing Logger")
        vbox = QVBoxLayout(self)
        if self.checkDb():
            self.__deliverable = Deliverable(self)
            self.__users = Users(self, self.__deliverable)
            vbox.addLayout(self.__deliverable.layout())
            self.__usersScroll = UsersScroll(self.__users, self)
            vbox.addWidget(self.__usersScroll)
        else:
            error = QLabel(self.db)
            error.setFont(self.getFont(16))
            vbox.addWidget(error)
        self.center()
        isMaximized = self.getWindowStateMaximized()
        if not isMaximized is None:
            if isMaximized:
                self.showMaximized()
     
    def changeEvent(self, QEvent):
        ParentWindow.changeEvent(self, QEvent)
        if self.isVisible():
            if self.__start:
                if self.checkDb():
                    search = SearchForm().searchNames("refresh")
                    refresh = self.__deliverable.searchObjects(search).mergeResults().results["refresh"]
                    refresh.setUsersForm(self.__users)
                    search = SearchForm().searchClasses(User)
                    users = self.__users.searchObjects(search).mergeResults().results
                    users = tuple(users.values())
                    for u in users:
                        u.setUsersFormScroll(self.__users, self.__usersScroll)
                    search = SearchForm().searchClasses(Header)
                    headers = self.__users.searchObjects(search).mergeResults().results
                    headers = tuple(headers.values())
                    for h in headers:
                        h.setUsersScroll(self.__usersScroll)
                    while self.__usersScroll.verticalScrollBar().isVisible():
                        self.setMinimumHeight(self.height()+1)
                    self.__usersScroll.setHorizontalScrollValue()
                self.__start = False
                
    def maximizeEvent(self, QEvent):
        self.updateWindowStateMaximized(True)
        
    def restoreEvent(self, QEvent):
        self.updateWindowStateMaximized(False)
                    
    def closeEvent(self, QEvent):
        ParentWindow.closeEvent(self, QEvent)
        if self.checkDb():
            self.db.callProcedure(None, "update_last_editor")
            self.db.query("select user_id, get_user(user_id) as user from last_editor")
            self.db.close()
    
    def __getId(self, table):
        if self.checkDb():
            self.db.query("select get_{}_id() as id".format(table))
            return self.db.results[2][0]["id"]
        return None
    
    def __updateTable(self, table, userId):
        if self.checkDb():
            if userId is None:
                self.db.callProcedure(None, "update_{}".format(table))
            else:
                self.db.callProcedure(None, "update_{}".format(table), userId)
            self.db.query("select user_id, get_user(user_id) as user from {}".format(table))
            return self.db.results[2][0]
        return None
            
    def getCurrentLeaderId(self):
        return self.__getId("current_leader")
  
    def getCurrentEditorId(self):
        return self.__getId("current_editor")
  
    def getLastEditorId(self):
        return self.__getId("last_editor")
  
    def updateCurrentLeader(self, userId):
        return self.__updateTable("current_leader", userId)
        
    def updateCurrentEditor(self, userId):
        return self.__updateTable("current_editor", userId)
        
    def updateLastEditor(self):
        return self.__updateTable("last_editor", None)
    
    def updateWindowStateMaximized(self, isMaximized):
        if self.checkDb():
            self.db.callProcedure(None, "update_logger_window_maximized", isMaximized)
            self.db.query("select get_logger_window_maximized() as maximized")
            return bool(self.db.results[2][0]["maximized"])
        return None
    
    def getWindowStateMaximized(self):
        if self.checkDb():
            self.db.query("select get_logger_window_maximized() as maximized")
            return bool(self.db.results[2][0]["maximized"])
        return None
        
    def updateHorizontalScroll(self, value):
        editorId = self.getCurrentEditorId()
        if not editorId is None:
            if editorId < 1:
                self.db.callProcedure(None, "update_users_horizontal_scroll", value)
                self.db.query("select horizontal from users_scroll")
                return self.db.results[2][0]["horizontal"]
        return None
            
    def getHorizontalScrollValue(self):
        editorId = self.getCurrentEditorId()
        if not editorId is None:
            if editorId < 1:
                self.db.query("select horizontal from users_scroll")
                return self.db.results[2][0]["horizontal"]
        return None

if __name__ == "__main__":
    Logger()
    #QtWorkbenchSql()