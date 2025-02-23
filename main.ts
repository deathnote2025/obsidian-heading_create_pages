import { App, Editor, MarkdownView, Modal, Notice, Plugin, PluginSettingTab, Setting, ButtonComponent } from 'obsidian';
import { exec } from 'child_process';
import { join } from 'path';

interface PythonTestPluginSettings {
	pythonPath: string;
}

const DEFAULT_SETTINGS: PythonTestPluginSettings = {
	pythonPath: 'python3'
}

export default class PythonTestPlugin extends Plugin {
	settings: PythonTestPluginSettings;

	private runPythonScript = () => {
		new InputModal(this.app, this).open();
	}

	private executeScript = (param1: string, param2: string) => {
		const scriptPath = join(this.app.vault.adapter.basePath, '.obsidian', 'plugins', 'Heading_Create_Pages', 'api.py');
		// 获取当前活动笔记的相对路径
		const activeFile = this.app.workspace.getActiveFile();
		const notePath = activeFile ? activeFile.path : '';
		exec(`${this.settings.pythonPath} "${scriptPath}" "${notePath}" "${param1}" `, (error, stdout, stderr) => {
			if (error) {
				new Notice('Error running Python script: ' + error.message);
				return;
			}
			if (stderr) {
				new Notice('Python script error: ' + stderr);
				return;
			}
			new Notice('Python script output: ' + stdout);
		});
	}

	onload = async () => {
		await this.loadSettings();

		// Add a ribbon icon for running Python script
		const ribbonIconEl = this.addRibbonIcon('code-glyph', 'Run Python Script', (evt: MouseEvent) => {
			this.runPythonScript();
		});
		ribbonIconEl.addClass('python-test-plugin-ribbon-class');

		// Add a command to run Python script
		this.addCommand({
			id: 'run-python-script',
			name: 'Run Python Script',
			callback: () => {
				this.runPythonScript();
			}
		});

		// Add settings tab
		this.addSettingTab(new PythonTestSettingTab(this.app, this));
	}

	onunload = () => {

	}

	loadSettings = async () => {
		this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
	}

	saveSettings = async () => {
		await this.saveData(this.settings);
	}
}

class InputModal extends Modal {
	param1: string = '';
	param2: string = '';
	plugin: PythonTestPlugin;

	constructor(app: App, plugin: PythonTestPlugin) {
		super(app);
		this.plugin = plugin;
	}

	onOpen() {
		const {contentEl} = this;

		contentEl.createEl('h2', {text: '输入参数'});
		new Setting(contentEl)
			.setName('Heading_levels')
      		.setDesc('向下拆解的层级（比如文章中有二级标题和三级标题，参数说明拆解这两层）')
			.addText(text => text
				.setValue(this.param1)
				.onChange(value => this.param1 = value));

		new Setting(contentEl)
			.addButton(btn => btn
				.setButtonText('运行')
				.setCta()
				.onClick(() => {
					this.close();
					this.plugin.executeScript(this.param1);
				}));
	}

	onClose() {
		const {contentEl} = this;
		contentEl.empty();
	}
}

class PythonTestSettingTab extends PluginSettingTab {
	plugin: PythonTestPlugin;

	constructor(app: App, plugin: PythonTestPlugin) {
		super(app, plugin);
		this.plugin = plugin;
	}

	display(): void {
		const {containerEl} = this;

		containerEl.empty();

		new Setting(containerEl)
			.setName('Python Path')
			.setDesc('Path to Python interpreter (e.g., python3)')
			.addText(text => text
				.setPlaceholder('python3')
				.setValue(this.plugin.settings.pythonPath)
				.onChange(async (value) => {
					this.plugin.settings.pythonPath = value;
					await this.plugin.saveSettings();
				}));
	}
}
