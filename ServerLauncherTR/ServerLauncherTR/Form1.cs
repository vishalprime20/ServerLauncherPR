using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace ServerLauncherTR
{
    public partial class Form1 : Form
    {
        AutoCompleteStringCollection coll = new AutoCompleteStringCollection();
        string[] folders;
        public Form1()
        {
            InitializeComponent();
            
            
            
        }

        private void txtSearchbox_TextChanged(object sender, EventArgs e)
        {
            if (txtSearchbox.TextLength > 1) {
                folders = System.IO.Directory.GetDirectories(@"Z:\Projects\", "PR#" + txtSearchbox.Text + "*", System.IO.SearchOption.TopDirectoryOnly);
                AutoCompleteStringCollection coll = new AutoCompleteStringCollection();
                //string[] folders = System.IO.Directory.GetDirectories(@"Z:\Projects\", "*", System.IO.SearchOption.TopDirectoryOnly);
                for (int i = 0; i < folders.Count(); i++)
                {
                    string folderName = folders[i].Replace("Z:\\Projects\\"+ "PR#", "");
                    //folderName = folderName.Replace("", "");
                    
                        coll.Add(folderName);
                    
                }

                txtSearchbox.AutoCompleteMode = AutoCompleteMode.Suggest;

                txtSearchbox.AutoCompleteSource = AutoCompleteSource.CustomSource;

                txtSearchbox.AutoCompleteCustomSource = coll;
            }
        }

        private void btnContractdrawing_Click(object sender, EventArgs e)
        {
            try
            {
                string Path = "Z:\\Projects\\" + "PR#" + txtSearchbox.Text + "\\1.0 Contract Drawings\\" + DateTime.Now.ToString("MM.dd.yyyy");
                System.Diagnostics.Process.Start(Path);
            }
            catch (Exception)
            {
                try
                {
                    string Path = "Z:\\Projects\\" + "PR#" + txtSearchbox.Text + "\\1.0 Contract Drawings\\";
                    System.Diagnostics.Process.Start(Path);
                }
                catch (Exception ex)
                {
                    MessageBox.Show("Exception catch here - Contractdrawing  : " + ex.ToString());
                }
            }
            
        }

        private void btnIncoming_Click(object sender, EventArgs e)
        {
            try
            {
                string Path = "Z:\\Projects\\" + "PR#" + txtSearchbox.Text + "\\2.0 Incoming\\";
                System.Diagnostics.Process.Start(Path);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Exception catch here - Incoming  : " + ex.ToString());
            }
        }

        private void btnWorking_Click(object sender, EventArgs e)
        {
            try
            {
                string Path = "Z:\\Projects\\" + "PR#" + txtSearchbox.Text + "\\3.0 Working\\";
                System.Diagnostics.Process.Start(Path);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Exception catch here - Working  : " + ex.ToString());
            }
        }

        private void btnOutgoing_Click(object sender, EventArgs e)
        {
            try
            {
                string Path = "Z:\\Projects\\" + "PR#" + txtSearchbox.Text + "\\4.0 Outgoing\\"+ DateTime.Now.ToString("yyyy")+"\\"+ DateTime.Now.ToString("MMMM yyyy") + "\\" + DateTime.Now.ToString("MM.dd.yyyy");
                System.Diagnostics.Process.Start(Path);
            }
            catch (Exception)
            {
                try
                {
                    string Path = "Z:\\Projects\\" + "PR#" + txtSearchbox.Text + "\\4.0 Outgoing\\" + DateTime.Now.ToString("yyyy") + "\\" + DateTime.Now.ToString("MMMM yyyy");
                    System.Diagnostics.Process.Start(Path);
                }
                catch (Exception)
                {
                    try
                    {
                        string Path = "Z:\\Projects\\" + "PR#" + txtSearchbox.Text + "\\4.0 Outgoing\\" + DateTime.Now.ToString("yyyy");
                        System.Diagnostics.Process.Start(Path);
                    }
                    catch (Exception ex1)
                    {
                        try
                        {
                            string Path = "Z:\\Projects\\" + "PR#" + txtSearchbox.Text + "\\4.0 Outgoing";
                            System.Diagnostics.Process.Start(Path);
                        }
                        catch (Exception ex)
                        {
                            MessageBox.Show("Exception catch here - Outgoing  : " + ex.ToString());
                        }
                    }
                }
            }
        }

        private void btnProjectDoc_Click(object sender, EventArgs e)
        {
            try
            {
                string Path = "Z:\\Projects\\" + "PR#" + txtSearchbox.Text + "\\5.0 Project Documentation\\";
                System.Diagnostics.Process.Start(Path);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Exception catch here - Project Documentation  : " + ex.ToString());
            }
        }
        
        private void btnListing_Click(object sender, EventArgs e)
        {
            try
            {
                string Path = "Z:\\Projects\\" + "PR#" + txtSearchbox.Text + "\\7.0 Listing\\";
                System.Diagnostics.Process.Start(Path);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Exception catch here - Listing  : " + ex.ToString());
            }
        }

        private void btnTracker_Click(object sender, EventArgs e)
        {
            
            try
            {
                string Path = "Z:\\Projects\\1.0 Project Tracker\\" + ("PR#" + txtSearchbox.Text).Split('_')[0] + "_Tracker.xls";
                System.Diagnostics.Process.Start(Path);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Exception catch here - Tracker  : " + ex.ToString());
            }
        }

        private void btnListLog_Click(object sender, EventArgs e)
        {
            try
            {
                string Path = "Z:\\Projects\\2.0 Project Listlog\\" + ("PR#" + txtSearchbox.Text).Split('_')[0] + "_Listlog.xls";
                System.Diagnostics.Process.Start(Path);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Exception catch here - ListLog  : " + ex.ToString());
            }
        }

        private void btnScheduler_Click(object sender, EventArgs e)
        {
            try
            {
                string Path = "Z:\\Projects\\3.0 Drawing Schedular\\" + ("PR#" + txtSearchbox.Text).Split('_')[0] + "_Schedular.xls";
                System.Diagnostics.Process.Start(Path);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Exception catch here - Scheduler  : " + ex.ToString());
            }
        }

        private void btnChangeOrder_Click(object sender, EventArgs e)
        {
            try
            {
                string Path = "Z:\\Projects\\4.0 Project Change_Order\\" + ("PR#" + txtSearchbox.Text).Split('_')[0] + "_Schedular.xls";
                System.Diagnostics.Process.Start(Path);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Exception catch here - ChangeOrder  : " + ex.ToString());
            }
        }

        private void label1_Click(object sender, EventArgs e)
        {

        }
    }
}
