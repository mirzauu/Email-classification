import Navigation from "@/components/Navigation";
import { Filter, Download, MoreVertical, GripVertical, Plus, X, Reply, ReplyAll, Forward, Archive, Trash2, MoreHorizontal, Check } from "lucide-react";
import { useState } from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Separator } from "@/components/ui/separator";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const insightTabs = [
  { id: "overview", name: "Overview" },
  { id: "inbox", name: "Inbox" },
  { id: "sent", name: "Sent" },
  { id: "archives", name: "Archives" },
  { id: "settings", name: "Settings" },
];

const initialRawCategories = [
  { id: "all", name: "All Payments", icon: "💳", enabled: true },
  { id: "subscriptions", name: "Subscriptions", icon: "🔄", enabled: true },
  { id: "invoices", name: "Invoices", icon: "📄", enabled: true },
  { id: "receipts", name: "Receipts", icon: "🧾", enabled: true },
  { id: "bills", name: "Bills & Utilities", icon: "💡", enabled: true },
  { id: "refunds", name: "Refunds", icon: "↩️", enabled: false },
];

const initialPaymentEmails = [
  { id: 1, from: "Netflix", subject: "Your payment was successful", amount: "$15.99", date: "Apr 28, 2025", category: "subscriptions" },
  { id: 2, from: "Spotify", subject: "Receipt for Premium subscription", amount: "$9.99", date: "Apr 27, 2025", category: "subscriptions" },
  { id: 3, from: "Amazon", subject: "Order confirmation #123-4567890", amount: "$43.50", date: "Apr 26, 2025", category: "receipts" },
  { id: 4, from: "Adobe", subject: "Creative Cloud invoice", amount: "$54.99", date: "Apr 25, 2025", category: "invoices" },
  { id: 5, from: "Apple", subject: "Your receipt from Apple", amount: "$0.99", date: "Apr 24, 2025", category: "receipts" },
  { id: 6, from: "GitHub", subject: "Payment receipt - Team plan", amount: "$44.00", date: "Apr 23, 2025", category: "subscriptions" },
  { id: 7, from: "Stripe", subject: "Payment successful for invoice", amount: "$120.00", date: "Apr 22, 2025", category: "invoices" },
  { id: 8, from: "Digital Ocean", subject: "Invoice for cloud services", amount: "$24.00", date: "Apr 21, 2025", category: "bills" },
];

const Finance = () => {
  const [activeView, setActiveView] = useState<"insight" | "raw">("insight");
  const [activeTab, setActiveTab] = useState("overview");
  const [isEditMode, setIsEditMode] = useState(false);
  const [rawCategories, setRawCategories] = useState(initialRawCategories);
  const [editingCategoryId, setEditingCategoryId] = useState<string | null>(null);
  const [selectedEmail, setSelectedEmail] = useState<any>(null);
  const [isEmailOpen, setIsEmailOpen] = useState(false);
  const [paymentEmails, setPaymentEmails] = useState(initialPaymentEmails);
  const [isAddPaymentOpen, setIsAddPaymentOpen] = useState(false);
  const [editingRowId, setEditingRowId] = useState<number | null>(null);
  const [editedPayment, setEditedPayment] = useState<any>(null);
  const [newPayment, setNewPayment] = useState({
    from: "",
    subject: "",
    amount: "",
    date: new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }),
    category: "all"
  });

  const handleAddCategory = () => {
    const newCategory = {
      id: `custom-${Date.now()}`,
      name: "New Category",
      icon: "📁",
      enabled: true,
    };
    setRawCategories([...rawCategories, newCategory]);
  };

  const handleDeleteCategory = (id: string) => {
    setRawCategories(rawCategories.filter(cat => cat.id !== id));
  };

  const handleToggleCategory = (id: string) => {
    setRawCategories(rawCategories.map(cat =>
      cat.id === id ? { ...cat, enabled: !cat.enabled } : cat
    ));
  };

  const handleRenameCategory = (id: string, newName: string) => {
    setRawCategories(rawCategories.map(cat =>
      cat.id === id ? { ...cat, name: newName } : cat
    ));
  };

  const handleMoveCategory = (index: number, direction: "up" | "down") => {
    const newCategories = [...rawCategories];
    const targetIndex = direction === "up" ? index - 1 : index + 1;
    if (targetIndex < 0 || targetIndex >= newCategories.length) return;
    
    [newCategories[index], newCategories[targetIndex]] = [newCategories[targetIndex], newCategories[index]];
    setRawCategories(newCategories);
  };

  const handleOpenEmail = (email: any) => {
    setSelectedEmail(email);
    setIsEmailOpen(true);
  };

  const handleAddPayment = () => {
    const payment = {
      id: paymentEmails.length + 1,
      from: newPayment.from,
      subject: newPayment.subject,
      amount: newPayment.amount,
      date: newPayment.date,
      category: newPayment.category
    };
    setPaymentEmails([payment, ...paymentEmails]);
    setIsAddPaymentOpen(false);
    setNewPayment({
      from: "",
      subject: "",
      amount: "",
      date: new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }),
      category: "all"
    });
  };

  const handleStartEdit = (email: any) => {
    setEditingRowId(email.id);
    setEditedPayment({ ...email });
  };

  const handleEditFieldChange = (field: string, value: string) => {
    setEditedPayment({ ...editedPayment, [field]: value });
  };

  const handleSaveEdit = () => {
    if (editedPayment) {
      setPaymentEmails(paymentEmails.map(email =>
        email.id === editedPayment.id ? editedPayment : email
      ));
    }
    setEditingRowId(null);
    setEditedPayment(null);
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <main className="flex h-[calc(100vh-88px)]">
        {/* Sidebar */}
        <aside className="w-64 border-r border-border bg-background px-4 py-6">
          <div className="mb-6 flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setActiveView("insight")}
                className={`text-lg font-semibold transition-colors ${
                  activeView === "insight"
                    ? "text-foreground"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Insight
              </button>
              <button
                onClick={() => setActiveView("raw")}
                className={`text-lg font-semibold transition-colors ${
                  activeView === "raw"
                    ? "text-foreground"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Raw
              </button>
            </div>
            {activeView === "raw" && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="p-1 hover:bg-muted rounded transition-colors">
                    <MoreVertical className="w-4 h-4 text-muted-foreground" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => setIsEditMode(!isEditMode)}>
                    {isEditMode ? "Done Editing" : "Edit"}
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>
          
          {activeView === "insight" ? (
            <nav className="space-y-2">
              {insightTabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full justify-start px-3 py-2 rounded-lg text-sm transition-colors ${
                    activeTab === tab.id
                      ? "bg-muted text-foreground"
                      : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                  }`}
                >
                  {tab.name}
                </button>
              ))}
            </nav>
          ) : (
            <div className="space-y-2">
              <nav className="space-y-2">
                {rawCategories
                  .filter(cat => isEditMode || cat.enabled)
                  .map((category, index) => (
                  <div
                    key={category.id}
                    className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                      !isEditMode && index === 0
                        ? "bg-muted text-foreground"
                        : category.enabled ? "text-muted-foreground hover:bg-muted/50 hover:text-foreground" : "text-muted-foreground/50"
                    } ${!category.enabled && !isEditMode ? 'hidden' : ''}`}
                  >
                    {isEditMode && (
                      <div className="flex flex-col gap-1">
                        <button
                          onClick={() => handleMoveCategory(rawCategories.indexOf(category), "up")}
                          disabled={rawCategories.indexOf(category) === 0}
                          className="p-0.5 hover:bg-muted rounded disabled:opacity-30"
                        >
                          <GripVertical className="w-3 h-3" />
                        </button>
                        <button
                          onClick={() => handleMoveCategory(rawCategories.indexOf(category), "down")}
                          disabled={rawCategories.indexOf(category) === rawCategories.length - 1}
                          className="p-0.5 hover:bg-muted rounded disabled:opacity-30"
                        >
                          <GripVertical className="w-3 h-3" />
                        </button>
                      </div>
                    )}
                    <span className="text-base">{category.icon}</span>
                    {editingCategoryId === category.id ? (
                      <Input
                        value={category.name}
                        onChange={(e) => handleRenameCategory(category.id, e.target.value)}
                        onBlur={() => setEditingCategoryId(null)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') setEditingCategoryId(null);
                        }}
                        autoFocus
                        className="h-6 text-sm"
                      />
                    ) : (
                      <button
                        onClick={() => !isEditMode && setActiveTab(category.id)}
                        onDoubleClick={() => isEditMode && setEditingCategoryId(category.id)}
                        className="flex-1 text-left"
                      >
                        {category.name}
                      </button>
                    )}
                    {isEditMode && (
                      <div className="flex items-center gap-1 ml-auto">
                        <Switch
                          checked={category.enabled}
                          onCheckedChange={() => handleToggleCategory(category.id)}
                        />
                      </div>
                    )}
                  </div>
                ))}
              </nav>
              {isEditMode && (
                <Button
                  onClick={handleAddCategory}
                  variant="outline"
                  size="sm"
                  className="w-full"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Category
                </Button>
              )}
            </div>
          )}
        </aside>

        {/* Main Content */}
        <div className="flex-1 px-8 py-6 overflow-y-auto">
          {activeView === "insight" ? (
            <div className="w-full h-full">
              {activeTab === "overview" && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-semibold text-foreground">Payment Overview</h2>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="border border-border rounded-lg p-6">
                      <div className="text-sm text-muted-foreground mb-2">Total This Month</div>
                      <div className="text-3xl font-bold text-foreground">$892.47</div>
                      <div className="text-xs text-green-500 mt-2">+12.5% from last month</div>
                    </div>
                    <div className="border border-border rounded-lg p-6">
                      <div className="text-sm text-muted-foreground mb-2">Active Subscriptions</div>
                      <div className="text-3xl font-bold text-foreground">24</div>
                      <div className="text-xs text-muted-foreground mt-2">8 new this month</div>
                    </div>
                    <div className="border border-border rounded-lg p-6">
                      <div className="text-sm text-muted-foreground mb-2">Pending Payments</div>
                      <div className="text-3xl font-bold text-foreground">3</div>
                      <div className="text-xs text-amber-500 mt-2">Due within 7 days</div>
                    </div>
                  </div>
                  <div className="border border-border rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-foreground mb-4">Recent Activity</h3>
                    <div className="space-y-3">
                      {[
                        { name: "Netflix", amount: "$15.99", status: "Completed", time: "2 hours ago" },
                        { name: "Spotify", amount: "$9.99", status: "Completed", time: "1 day ago" },
                        { name: "Amazon", amount: "$43.50", status: "Completed", time: "2 days ago" },
                      ].map((item, i) => (
                        <div key={i} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center">
                              💳
                            </div>
                            <div>
                              <div className="text-sm font-medium text-foreground">{item.name}</div>
                              <div className="text-xs text-muted-foreground">{item.time}</div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-sm font-semibold text-foreground">{item.amount}</div>
                            <div className="text-xs text-green-500">{item.status}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "inbox" && (
                <div className="space-y-4">
                  <h2 className="text-2xl font-semibold text-foreground">Inbox (12)</h2>
                  <div className="border border-border rounded-lg overflow-hidden">
                    {[
                      { from: "PayPal", subject: "You've received a payment", preview: "You received $250.00 from John Doe", time: "10:30 AM", unread: true },
                      { from: "Stripe", subject: "New invoice available", preview: "Your invoice #INV-2025-0428 is ready", time: "Yesterday", unread: true },
                      { from: "Square", subject: "Payment confirmation", preview: "Payment of $89.99 processed successfully", time: "2 days ago", unread: false },
                      { from: "Venmo", subject: "Payment received", preview: "Sarah sent you $45.00", time: "3 days ago", unread: false },
                    ].map((email, i) => (
                      <div key={i} className={`p-4 border-b border-border/50 last:border-0 hover:bg-muted/50 cursor-pointer ${email.unread ? 'bg-muted/30' : ''}`}>
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            {email.unread && <div className="w-2 h-2 rounded-full bg-primary" />}
                            <span className="text-sm font-semibold text-foreground">{email.from}</span>
                          </div>
                          <span className="text-xs text-muted-foreground">{email.time}</span>
                        </div>
                        <div className="text-sm font-medium text-foreground mb-1">{email.subject}</div>
                        <div className="text-xs text-muted-foreground">{email.preview}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === "sent" && (
                <div className="space-y-4">
                  <h2 className="text-2xl font-semibold text-foreground">Sent Emails (5)</h2>
                  <div className="border border-border rounded-lg overflow-hidden">
                    {[
                      { to: "support@netflix.com", subject: "Request for refund", preview: "I would like to request a refund for...", time: "Apr 25", status: "Replied" },
                      { to: "billing@adobe.com", subject: "Invoice inquiry", preview: "Could you please clarify the charge for...", time: "Apr 23", status: "Read" },
                      { to: "payments@spotify.com", subject: "Payment method update", preview: "I need to update my payment method...", time: "Apr 20", status: "Sent" },
                    ].map((email, i) => (
                      <div key={i} className="p-4 border-b border-border/50 last:border-0 hover:bg-muted/50 cursor-pointer">
                        <div className="flex items-start justify-between mb-2">
                          <span className="text-sm font-semibold text-foreground">To: {email.to}</span>
                          <div className="flex items-center gap-2">
                            <span className="text-xs px-2 py-1 rounded-full bg-muted text-muted-foreground">{email.status}</span>
                            <span className="text-xs text-muted-foreground">{email.time}</span>
                          </div>
                        </div>
                        <div className="text-sm font-medium text-foreground mb-1">{email.subject}</div>
                        <div className="text-xs text-muted-foreground">{email.preview}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === "archives" && (
                <div className="space-y-4">
                  <h2 className="text-2xl font-semibold text-foreground">Archives (48)</h2>
                  <div className="border border-border rounded-lg overflow-hidden">
                    {[
                      { from: "Amazon Prime", subject: "Your membership renewal", date: "Mar 28, 2025", amount: "$14.99" },
                      { from: "Apple Music", subject: "Receipt for subscription", date: "Mar 15, 2025", amount: "$10.99" },
                      { from: "GitHub Pro", subject: "Payment successful", date: "Mar 1, 2025", amount: "$7.00" },
                      { from: "Dropbox Plus", subject: "Monthly invoice", date: "Feb 28, 2025", amount: "$11.99" },
                      { from: "Notion", subject: "Personal Pro renewal", date: "Feb 15, 2025", amount: "$8.00" },
                    ].map((email, i) => (
                      <div key={i} className="p-4 border-b border-border/50 last:border-0 hover:bg-muted/50 cursor-pointer">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-sm font-semibold text-foreground">{email.from}</span>
                              <span className="text-xs text-muted-foreground">• {email.date}</span>
                            </div>
                            <div className="text-sm text-muted-foreground">{email.subject}</div>
                          </div>
                          <div className="text-sm font-semibold text-foreground">{email.amount}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === "settings" && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-semibold text-foreground">Email Settings</h2>
                  
                  <div className="border border-border rounded-lg p-6 space-y-6">
                    <div>
                      <h3 className="text-lg font-semibold text-foreground mb-4">Notifications</h3>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="text-sm font-medium text-foreground">Payment alerts</div>
                            <div className="text-xs text-muted-foreground">Get notified about new payments</div>
                          </div>
                          <div className="w-10 h-6 bg-primary rounded-full" />
                        </div>
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="text-sm font-medium text-foreground">Weekly summary</div>
                            <div className="text-xs text-muted-foreground">Receive weekly payment summaries</div>
                          </div>
                          <div className="w-10 h-6 bg-muted rounded-full" />
                        </div>
                      </div>
                    </div>

                    <div className="border-t border-border pt-6">
                      <h3 className="text-lg font-semibold text-foreground mb-4">Email Categories</h3>
                      <div className="space-y-2">
                        <div className="text-sm text-muted-foreground">Automatically categorize payment emails</div>
                        <div className="flex flex-wrap gap-2 mt-3">
                          {["Subscriptions", "Invoices", "Receipts", "Bills", "Refunds"].map((cat) => (
                            <span key={cat} className="px-3 py-1 bg-muted rounded-full text-xs text-foreground">{cat}</span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <>
              <div className="flex items-center justify-between mb-6">
                <div className="text-sm text-muted-foreground">
                  Last synced Apr 28th, 2025
                </div>
                <div className="flex items-center gap-3">
                  <Button onClick={() => setIsAddPaymentOpen(true)} size="sm">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Payment
                  </Button>
                  <button className="p-2 hover:bg-muted rounded-lg transition-colors">
                    <Filter className="w-5 h-5 text-foreground" />
                  </button>
                  <button className="p-2 hover:bg-muted rounded-lg transition-colors">
                    <Download className="w-5 h-5 text-foreground" />
                  </button>
                </div>
              </div>

              {/* Payment Emails Table */}
              <div className="border border-border rounded-lg overflow-hidden">
                <div className="bg-muted/30">
                  <div className={`grid ${editingRowId !== null ? 'grid-cols-7' : 'grid-cols-6'} gap-4 px-6 py-3 border-b border-border`}>
                    <div className="text-sm font-medium text-foreground">From</div>
                    <div className="text-sm font-medium text-foreground col-span-2">Subject</div>
                    <div className="text-sm font-medium text-foreground">Amount</div>
                    <div className="text-sm font-medium text-foreground">Date</div>
                    {editingRowId !== null && (
                      <div className="text-sm font-medium text-foreground">Category</div>
                    )}
                    <div className="text-sm font-medium text-foreground">Actions</div>
                  </div>
                </div>
                
                {/* Table Body - Sample payment emails */}
                <div className="bg-background min-h-[500px]">
                  {paymentEmails.map((email, i) => (
                    <div
                      key={i}
                      className={`grid ${editingRowId !== null ? 'grid-cols-7' : 'grid-cols-6'} gap-4 px-6 py-4 border-b border-border/50 hover:bg-muted/50 transition-colors`}
                    >
                      {editingRowId === email.id && editedPayment ? (
                        <>
                          <div className="flex items-center" onClick={(e) => e.stopPropagation()}>
                            <Input 
                              value={editedPayment.from} 
                              onChange={(e) => handleEditFieldChange('from', e.target.value)}
                              className="h-8 text-sm"
                            />
                          </div>
                          <div className="col-span-2 flex items-center" onClick={(e) => e.stopPropagation()}>
                            <Input 
                              value={editedPayment.subject} 
                              onChange={(e) => handleEditFieldChange('subject', e.target.value)}
                              className="h-8 text-sm"
                            />
                          </div>
                          <div className="flex items-center" onClick={(e) => e.stopPropagation()}>
                            <Input 
                              value={editedPayment.amount} 
                              onChange={(e) => handleEditFieldChange('amount', e.target.value)}
                              className="h-8 text-sm"
                            />
                          </div>
                          <div className="flex items-center" onClick={(e) => e.stopPropagation()}>
                            <Input 
                              value={editedPayment.date} 
                              onChange={(e) => handleEditFieldChange('date', e.target.value)}
                              className="h-8 text-sm"
                            />
                          </div>
                          <div className="flex items-center" onClick={(e) => e.stopPropagation()}>
                            <Select value={editedPayment.category} onValueChange={(value) => handleEditFieldChange('category', value)}>
                              <SelectTrigger className="h-8 text-sm">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent className="bg-popover">
                                {rawCategories.filter(cat => cat.enabled).map((category) => (
                                  <SelectItem key={category.id} value={category.id}>
                                    <span className="flex items-center gap-2">
                                      <span>{category.icon}</span>
                                      <span>{category.name}</span>
                                    </span>
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>
                        </>
                      ) : (
                        <div 
                          className="col-span-5 grid grid-cols-5 gap-4 text-sm text-foreground font-medium cursor-pointer"
                          onClick={() => handleOpenEmail(email)}
                        >
                          <div>{email.from}</div>
                          <div className="col-span-2">{email.subject}</div>
                          <div className="font-semibold">{email.amount}</div>
                          <div className="text-muted-foreground">{email.date}</div>
                        </div>
                      )}
                      <div className="flex items-center justify-center gap-2">
                        {editingRowId === email.id ? (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleSaveEdit();
                            }}
                            className="p-1.5 hover:bg-muted rounded-lg transition-colors text-green-600"
                          >
                            <Check className="w-4 h-4" />
                          </button>
                        ) : (
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <button 
                                className="p-1.5 hover:bg-muted rounded-lg transition-colors"
                                onClick={(e) => e.stopPropagation()}
                              >
                                <MoreVertical className="w-4 h-4 text-muted-foreground" />
                              </button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end" className="bg-background">
                              <DropdownMenuItem 
                                className="cursor-pointer"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleStartEdit(email);
                                }}
                              >
                                Edit
                              </DropdownMenuItem>
                              <DropdownMenuItem className="cursor-pointer text-destructive">
                                Delete
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </main>

      {/* Email Dialog */}
      <Dialog open={isEmailOpen} onOpenChange={setIsEmailOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          {selectedEmail && (
            <div className="space-y-4">
              {/* Email Header */}
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <h2 className="text-2xl font-semibold text-foreground">{selectedEmail.subject}</h2>
                </div>
                
                {/* Action Buttons */}
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm">
                    <Reply className="w-4 h-4 mr-2" />
                    Reply
                  </Button>
                  <Button variant="outline" size="sm">
                    <ReplyAll className="w-4 h-4 mr-2" />
                    Reply All
                  </Button>
                  <Button variant="outline" size="sm">
                    <Forward className="w-4 h-4 mr-2" />
                    Forward
                  </Button>
                  <div className="ml-auto flex gap-2">
                    <Button variant="ghost" size="sm">
                      <Archive className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="sm">
                      <Trash2 className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="sm">
                      <MoreHorizontal className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>

              <Separator />

              {/* Sender Info */}
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-semibold">
                    {selectedEmail.from.charAt(0)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm font-semibold text-foreground">{selectedEmail.from}</div>
                        <div className="text-xs text-muted-foreground">to me</div>
                      </div>
                      <div className="text-xs text-muted-foreground">{selectedEmail.date}</div>
                    </div>
                  </div>
                </div>
              </div>

              <Separator />

              {/* Email Body */}
              <div className="space-y-4 py-4">
                <div className="text-sm text-foreground leading-relaxed">
                  <p className="mb-4">Hi there,</p>
                  <p className="mb-4">
                    Thank you for your payment of <strong>{selectedEmail.amount}</strong>. 
                    Your transaction has been completed successfully.
                  </p>
                  <p className="mb-4">
                    <strong>Transaction Details:</strong>
                  </p>
                  <div className="bg-muted/50 rounded-lg p-4 mb-4 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">From:</span>
                      <span className="font-medium">{selectedEmail.from}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Amount:</span>
                      <span className="font-semibold">{selectedEmail.amount}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Date:</span>
                      <span>{selectedEmail.date}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Status:</span>
                      <span className="text-green-600">Completed</span>
                    </div>
                  </div>
                  <p className="mb-4">
                    You can view your receipt and transaction history in your account dashboard.
                  </p>
                  <p className="mb-4">
                    If you have any questions or concerns about this transaction, please don't hesitate to contact our support team.
                  </p>
                  <p className="mb-4">
                    Best regards,<br />
                    <strong>{selectedEmail.from} Team</strong>
                  </p>
                </div>
              </div>

              <Separator />

              {/* Reply Section */}
              <div className="pt-4">
                <Button variant="outline" className="w-full">
                  <Reply className="w-4 h-4 mr-2" />
                  Click to Reply
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Add Payment Dialog */}
      <Dialog open={isAddPaymentOpen} onOpenChange={setIsAddPaymentOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Add New Payment</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">From</label>
              <Input
                placeholder="Enter company/person name"
                value={newPayment.from}
                onChange={(e) => setNewPayment({ ...newPayment, from: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Subject</label>
              <Input
                placeholder="Enter payment subject"
                value={newPayment.subject}
                onChange={(e) => setNewPayment({ ...newPayment, subject: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Amount</label>
              <Input
                placeholder="$0.00"
                value={newPayment.amount}
                onChange={(e) => setNewPayment({ ...newPayment, amount: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Date</label>
              <Input
                type="text"
                value={newPayment.date}
                onChange={(e) => setNewPayment({ ...newPayment, date: e.target.value })}
              />
            </div>
          </div>
          <div className="flex gap-3 justify-end">
            <Button variant="outline" onClick={() => setIsAddPaymentOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleAddPayment}>
              Add Payment
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Finance;
