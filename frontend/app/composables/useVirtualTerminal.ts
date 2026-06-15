import { ref } from 'vue'

interface FSEntry {
  type: 'file' | 'dir'
  content?: string
  children?: Record<string, FSEntry>
  createdAt?: string
  size?: number
}

export function useVirtualTerminal() {
  const currentDir = ref('/home/user')
  const history = ref<{ command: string; output: string; error?: boolean }[]>([])

  // Seed File System
  const initialFs = (): FSEntry => ({
    type: 'dir',
    children: {
      home: {
        type: 'dir',
        children: {
          user: {
            type: 'dir',
            children: {
              projects: {
                type: 'dir',
                children: {
                  'quiz_app': {
                    type: 'dir',
                    children: {
                      'AGENTS.md': {
                        type: 'file',
                        content: '# LinuxMaster Project\nThis is an interactive platform.',
                        size: 56
                      }
                    }
                  }
                }
              },
              'welcome.txt': {
                type: 'file',
                content: 'Welcome to LinuxMaster virtual terminal sandbox!\nTry typing commands like:\n- ls -la\n- pwd\n- mkdir code\n- touch index.py\n- wc -l welcome.txt',
                size: 142
              },
              'syslog.log': {
                type: 'file',
                content: 'Jun 14 12:00:01 kernel: Booting Linux version 5.15.0\nJun 14 12:00:02 systemd: Starting Network Manager...\nJun 14 12:00:03 systemd: Reached target Multi-User System.\nJun 14 12:00:04 sshd: Server listening on port 22.',
                size: 215
              }
            }
          }
        }
      },
      bin: {
        type: 'dir',
        children: {
          'bash': { type: 'file', content: 'BINARY BASH', size: 1048576 }
        }
      }
    }
  })

  const fileSystem = ref<FSEntry>(initialFs())

  function resetFs() {
    fileSystem.value = initialFs()
    currentDir.value = '/home/user'
    history.value = []
  }

  // Resolve path helper
  function resolvePath(pathStr: string): { entry: FSEntry | null; parent: FSEntry | null; name: string } {
    let parts: string[] = []
    
    if (pathStr.startsWith('/')) {
      parts = pathStr.split('/').filter(Boolean)
    } else {
      const currentParts = currentDir.value.split('/').filter(Boolean)
      parts = [...currentParts, ...pathStr.split('/').filter(Boolean)]
    }

    const resolvedParts: string[] = []
    for (const p of parts) {
      if (p === '..') {
        resolvedParts.pop()
      } else if (p !== '.') {
        resolvedParts.push(p)
      }
    }

    let current: FSEntry = fileSystem.value
    let parent: FSEntry | null = null
    let name = ''

    for (let i = 0; i < resolvedParts.length; i++) {
      const part = resolvedParts[i]
      if (current.type !== 'dir' || !current.children || !current.children[part]) {
        return { entry: null, parent: null, name: part }
      }
      parent = current
      current = current.children[part]
      name = part
    }

    return { entry: current, parent, name }
  }

  function executeCommand(cmdLine: string): string {
    const trimmed = cmdLine.trim()
    if (!trimmed) return ''

    const parts = trimmed.split(/\s+/)
    const cmd = parts[0]
    const args = parts.slice(1)

    const logHistory = (output: string, error = false) => {
      history.value.push({ command: cmdLine, output, error })
    }

    try {
      switch (cmd) {
        case 'clear':
          history.value = []
          return ''
          
        case 'help': {
          const helpMsg = `Supported Commands:\n  pwd, ls, cd, mkdir, rmdir, touch, cp, mv, rm, cat, head, tail, sort, uniq, wc, grep, clear, help`
          logHistory(helpMsg)
          return helpMsg
        }

        case 'pwd': {
          logHistory(currentDir.value)
          return currentDir.value
        }

        case 'ls': {
          let showHidden = false
          let longFormat = false
          const paths: string[] = []

          for (const arg of args) {
            if (arg.startsWith('-')) {
              for (const char of arg.slice(1)) {
                if (char === 'a') showHidden = true
                if (char === 'l') longFormat = true
              }
            } else {
              paths.push(arg)
            }
          }

          const targetPath = paths[0] || '.'
          const { entry } = resolvePath(targetPath)

          if (!entry) {
            const err = `ls: cannot access '${targetPath}': No such file or directory`
            logHistory(err, true)
            return err
          }

          if (entry.type === 'file') {
            const out = longFormat ? `-rw-r--r-- 1 user user ${entry.size || 0} Jun 14 ${targetPath}` : targetPath
            logHistory(out)
            return out
          }

          const children = entry.children || {}
          let items = Object.keys(children)
          
          if (!showHidden) {
            items = items.filter(name => !name.startsWith('.'))
          } else {
            items = ['.', '..', ...items]
          }

          if (longFormat) {
            const lines = items.map(name => {
              let details = ''
              if (name === '.' || name === '..') {
                details = `drwxr-xr-x 2 user user 4096 Jun 14 ${name}`
              } else {
                const child = children[name]
                if (child.type === 'dir') {
                  details = `drwxr-xr-x 2 user user 4096 Jun 14 ${name}`
                } else {
                  details = `-rw-r--r-- 1 user user ${child.size || 0} Jun 14 ${name}`
                }
              }
              return details
            })
            const out = lines.join('\n')
            logHistory(out)
            return out
          } else {
            const out = items.join('  ')
            logHistory(out)
            return out
          }
        }

        case 'cd': {
          const target = args[0] || '/home/user'
          const { entry } = resolvePath(target)

          if (!entry) {
            const err = `-bash: cd: ${target}: No such file or directory`
            logHistory(err, true)
            return err
          }

          if (entry.type !== 'dir') {
            const err = `-bash: cd: ${target}: Not a directory`
            logHistory(err, true)
            return err
          }

          let parts: string[] = []
          if (target.startsWith('/')) {
            parts = target.split('/').filter(Boolean)
          } else {
            const currentParts = currentDir.value.split('/').filter(Boolean)
            parts = [...currentParts, ...target.split('/').filter(Boolean)]
          }

          const resolvedParts: string[] = []
          for (const p of parts) {
            if (p === '..') {
              resolvedParts.pop()
            } else if (p !== '.') {
              resolvedParts.push(p)
            }
          }

          currentDir.value = '/' + resolvedParts.join('/')
          logHistory('')
          return ''
        }

        case 'mkdir': {
          const name = args[0]
          if (!name) {
            const err = `mkdir: missing operand`
            logHistory(err, true)
            return err
          }

          const { entry } = resolvePath(name)
          if (entry) {
            const err = `mkdir: cannot create directory '${name}': File exists`
            logHistory(err, true)
            return err
          }

          const lastSlashIndex = name.lastIndexOf('/')
          let parentPath = '.'
          let targetName = name
          if (lastSlashIndex !== -1) {
            parentPath = name.slice(0, lastSlashIndex)
            targetName = name.slice(lastSlashIndex + 1)
          }

          const parentResolution = resolvePath(parentPath)
          if (!parentResolution.entry || parentResolution.entry.type !== 'dir') {
            const err = `mkdir: cannot create directory '${name}': No such file or directory`
            logHistory(err, true)
            return err
          }

          if (!parentResolution.entry.children) {
            parentResolution.entry.children = {}
          }

          parentResolution.entry.children[targetName] = {
            type: 'dir',
            children: {}
          }
          logHistory('')
          return ''
        }

        case 'rmdir': {
          const name = args[0]
          if (!name) {
            const err = `rmdir: missing operand`
            logHistory(err, true)
            return err
          }

          const { entry, parent, name: dirName } = resolvePath(name)
          if (!entry) {
            const err = `rmdir: failed to remove '${name}': No such file or directory`
            logHistory(err, true)
            return err
          }

          if (entry.type !== 'dir') {
            const err = `rmdir: failed to remove '${name}': Not a directory`
            logHistory(err, true)
            return err
          }

          if (entry.children && Object.keys(entry.children).length > 0) {
            const err = `rmdir: failed to remove '${name}': Directory not empty`
            logHistory(err, true)
            return err
          }

          if (parent && parent.children) {
            delete parent.children[dirName]
          }
          logHistory('')
          return ''
        }

        case 'touch': {
          const name = args[0]
          if (!name) {
            const err = `touch: missing file operand`
            logHistory(err, true)
            return err
          }

          const { entry } = resolvePath(name)
          if (entry) {
            logHistory('')
            return ''
          }

          const lastSlashIndex = name.lastIndexOf('/')
          let parentPath = '.'
          let targetName = name
          if (lastSlashIndex !== -1) {
            parentPath = name.slice(0, lastSlashIndex)
            targetName = name.slice(lastSlashIndex + 1)
          }

          const parentResolution = resolvePath(parentPath)
          if (!parentResolution.entry || parentResolution.entry.type !== 'dir') {
            const err = `touch: cannot touch '${name}': No such file or directory`
            logHistory(err, true)
            return err
          }

          if (!parentResolution.entry.children) {
            parentResolution.entry.children = {}
          }

          parentResolution.entry.children[targetName] = {
            type: 'file',
            content: '',
            size: 0
          }
          logHistory('')
          return ''
        }

        case 'cat': {
          const name = args[0]
          if (!name) {
            const err = `cat: missing file operand`
            logHistory(err, true)
            return err
          }

          const { entry } = resolvePath(name)
          if (!entry) {
            const err = `cat: ${name}: No such file or directory`
            logHistory(err, true)
            return err
          }

          if (entry.type === 'dir') {
            const err = `cat: ${name}: Is a directory`
            logHistory(err, true)
            return err
          }

          logHistory(entry.content || '')
          return entry.content || ''
        }

        case 'head': {
          const name = args[0]
          if (!name) {
            const err = `head: missing file operand`
            logHistory(err, true)
            return err
          }
          const { entry } = resolvePath(name)
          if (!entry || entry.type === 'dir') {
            const err = `head: cannot open '${name}'`
            logHistory(err, true)
            return err
          }
          const lines = (entry.content || '').split('\n').slice(0, 10).join('\n')
          logHistory(lines)
          return lines
        }

        case 'tail': {
          const name = args[0]
          if (!name) {
            const err = `tail: missing file operand`
            logHistory(err, true)
            return err
          }
          const { entry } = resolvePath(name)
          if (!entry || entry.type === 'dir') {
            const err = `tail: cannot open '${name}'`
            logHistory(err, true)
            return err
          }
          const allLines = (entry.content || '').split('\n')
          const lines = allLines.slice(Math.max(0, allLines.length - 10)).join('\n')
          logHistory(lines)
          return lines
        }

        case 'wc': {
          let countLines = false
          let countWords = false
          let countBytes = false
          const files: string[] = []

          for (const arg of args) {
            if (arg.startsWith('-')) {
              for (const char of arg.slice(1)) {
                if (char === 'l') countLines = true
                if (char === 'w') countWords = true
                if (char === 'c') countBytes = true
              }
            } else {
              files.push(arg)
            }
          }

          if (!countLines && !countWords && !countBytes) {
            countLines = true
            countWords = true
            countBytes = true
          }

          const name = files[0]
          if (!name) {
            const err = `wc: missing file operand`
            logHistory(err, true)
            return err
          }

          const { entry } = resolvePath(name)
          if (!entry || entry.type === 'dir') {
            const err = `wc: ${name}: No such file or directory`
            logHistory(err, true)
            return err
          }

          const text = entry.content || ''
          const lines = text.split('\n').length - 1
          const words = text.split(/\s+/).filter(Boolean).length
          const bytes = text.length

          const results: string[] = []
          if (countLines) results.push(lines.toString())
          if (countWords) results.push(words.toString())
          if (countBytes) results.push(bytes.toString())
          results.push(name)

          const out = results.join(' ')
          logHistory(out)
          return out
        }

        case 'rm': {
          let recursive = false
          const files: string[] = []

          for (const arg of args) {
            if (arg === '-r' || arg === '-rf' || arg === '--recursive') {
              recursive = true
            } else if (!arg.startsWith('-')) {
              files.push(arg)
            }
          }

          const name = files[0]
          if (!name) {
            const err = `rm: missing operand`
            logHistory(err, true)
            return err
          }

          const { entry, parent, name: elementName } = resolvePath(name)
          if (!entry) {
            const err = `rm: cannot remove '${name}': No such file or directory`
            logHistory(err, true)
            return err
          }

          if (entry.type === 'dir' && !recursive) {
            const err = `rm: cannot remove '${name}': Is a directory`
            logHistory(err, true)
            return err
          }

          if (parent && parent.children) {
            delete parent.children[elementName]
          }
          logHistory('')
          return ''
        }

        case 'grep': {
          if (args.length < 2) {
            const err = `Usage: grep [pattern] [file]`
            logHistory(err, true)
            return err
          }
          const pattern = args[0]
          const fileName = args[1]
          const { entry } = resolvePath(fileName)

          if (!entry || entry.type === 'dir') {
            const err = `grep: ${fileName}: No such file or directory`
            logHistory(err, true)
            return err
          }

          const lines = (entry.content || '').split('\n')
          const matches = lines.filter(l => l.toLowerCase().includes(pattern.toLowerCase()))
          
          const out = matches.join('\n')
          logHistory(out)
          return out
        }

        case 'cp': {
          if (args.length < 2) {
            const err = `cp: missing file operand`
            logHistory(err, true)
            return err
          }
          const src = args[0]
          const dest = args[1]
          const srcRes = resolvePath(src)
          
          if (!srcRes.entry || srcRes.entry.type === 'dir') {
            const err = `cp: cannot copy '${src}': No such file`
            logHistory(err, true)
            return err
          }

          const destRes = resolvePath(dest)
          
          if (destRes.entry && destRes.entry.type === 'dir') {
            if (!destRes.entry.children) destRes.entry.children = {}
            destRes.entry.children[srcRes.name] = { ...srcRes.entry }
          } else {
            const lastSlash = dest.lastIndexOf('/')
            let destParent = '.'
            let destName = dest
            if (lastSlash !== -1) {
              destParent = dest.slice(0, lastSlash)
              destName = dest.slice(lastSlash + 1)
            }
            const parentRes = resolvePath(destParent)
            if (!parentRes.entry || parentRes.entry.type !== 'dir') {
              const err = `cp: cannot copy to '${dest}': Parent directory not found`
              logHistory(err, true)
              return err
            }
            if (!parentRes.entry.children) parentRes.entry.children = {}
            parentRes.entry.children[destName] = { ...srcRes.entry }
          }
          logHistory('')
          return ''
        }

        case 'mv': {
          if (args.length < 2) {
            const err = `mv: missing file operand`
            logHistory(err, true)
            return err
          }
          const src = args[0]
          const dest = args[1]
          const srcRes = resolvePath(src)
          
          if (!srcRes.entry) {
            const err = `mv: cannot stat '${src}': No such file or directory`
            logHistory(err, true)
            return err
          }

          const destRes = resolvePath(dest)
          
          if (srcRes.parent && srcRes.parent.children) {
            delete srcRes.parent.children[srcRes.name]
          }

          if (destRes.entry && destRes.entry.type === 'dir') {
            if (!destRes.entry.children) destRes.entry.children = {}
            destRes.entry.children[srcRes.name] = srcRes.entry
          } else {
            const lastSlash = dest.lastIndexOf('/')
            let destParent = '.'
            let destName = dest
            if (lastSlash !== -1) {
              destParent = dest.slice(0, lastSlash)
              destName = dest.slice(lastSlash + 1)
            }
            const parentRes = resolvePath(destParent)
            if (parentRes.entry && parentRes.entry.type === 'dir') {
              if (!parentRes.entry.children) parentRes.entry.children = {}
              parentRes.entry.children[destName] = srcRes.entry
            }
          }
          logHistory('')
          return ''
        }

        default: {
          const err = `-bash: ${cmd}: command not found`
          logHistory(err, true)
          return err
        }
      }
    } catch (e: any) {
      const err = `An execution error occurred: ${e.message}`
      logHistory(err, true)
      return err
    }
  }

  return {
    currentDir,
    history,
    fileSystem,
    resetFs,
    executeCommand
  }
}
