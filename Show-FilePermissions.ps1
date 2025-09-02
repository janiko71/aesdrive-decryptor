function Show-FilePermissions {
    param([string]$FilePath)
    
    if (-not (Test-Path $FilePath)) {
        Write-Error "Fichier non trouve: $FilePath"
        return
    }
    
    $file = Get-Item $FilePath
    $acl = Get-Acl $FilePath
    
    Write-Host ("=" * 60) -ForegroundColor Magenta
    Write-Host "ANALYSE DES PERMISSIONS: $($file.Name)" -ForegroundColor Magenta
    Write-Host ("=" * 60) -ForegroundColor Magenta
    
    # Informations generales
    Write-Host ""
    Write-Host "INFORMATIONS GENERALES:" -ForegroundColor Yellow
    Write-Host "  Chemin complet: $($file.FullName)"
    Write-Host "  Taille: $($file.Length) bytes"
    Write-Host "  Cree: $($file.CreationTime)"
    Write-Host "  Modifie: $($file.LastWriteTime)"
    Write-Host "  Attributs: $($file.Attributes)"
    
    # Proprietes de securite
    Write-Host ""
    Write-Host "PROPRIETES DE SECURITE:" -ForegroundColor Yellow
    Write-Host "  Proprietaire: $($acl.Owner)" -ForegroundColor Green
    if ($acl.Group) {
        Write-Host "  Groupe: $($acl.Group)" -ForegroundColor Green
    }
    Write-Host "  Controle d'acces protege: $($acl.AccessRuleProtected)"
    Write-Host "  Audit protege: $($acl.AuditRuleProtected)"
    
    # Permissions detaillees
    Write-Host ""
    Write-Host "PERMISSIONS DETAILLEES:" -ForegroundColor Yellow
    
    foreach ($access in $acl.Access) {
        $typeColor = if ($access.AccessControlType -eq "Allow") { "Green" } else { "Red" }
        
        Write-Host "  +-- Utilisateur/Groupe: $($access.IdentityReference)" -ForegroundColor Cyan
        Write-Host "  |   Type d'acces: $($access.AccessControlType)" -ForegroundColor $typeColor
        Write-Host "  |   Droits: $($access.FileSystemRights)" -ForegroundColor White
        Write-Host "  |   Herite: $($access.IsInherited)" -ForegroundColor Gray
        Write-Host "  |   Propagation: $($access.InheritanceFlags)" -ForegroundColor Gray
        Write-Host "  +----------------------------------------" -ForegroundColor Gray
    }
    
    # Droits de l'utilisateur actuel
    Write-Host ""
    Write-Host "DROITS DE L'UTILISATEUR ACTUEL:" -ForegroundColor Yellow
    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    Write-Host "  Utilisateur: $currentUser" -ForegroundColor Cyan
    
    # Test des droits specifiques
    try {
        # Test lecture
        $canRead = Test-Path $FilePath -PathType Leaf
        $readColor = if ($canRead) { "Green" } else { "Red" }
        Write-Host "  Lecture: $canRead" -ForegroundColor $readColor
        
        # Test ecriture (approximatif)
        $canWrite = -not (Get-Item $FilePath).IsReadOnly
        $writeColor = if ($canWrite) { "Green" } else { "Red" }
        Write-Host "  Ecriture: $canWrite" -ForegroundColor $writeColor
        
        # Test executable
        $executableExtensions = @('.exe', '.bat', '.cmd', '.ps1', '.com', '.msi', '.scr', '.vbs', '.js')
        $canExecute = $file.Extension.ToLower() -in $executableExtensions
        $execColor = if ($canExecute) { "Green" } else { "Gray" }
        Write-Host "  Executable: $canExecute" -ForegroundColor $execColor
        
    } catch {
        Write-Host "  Erreur lors du test des droits: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
}

# Version simplifiee pour affichage rapide
function Get-FilePermissionsSimple {
    param([string]$FilePath)
    
    if (-not (Test-Path $FilePath)) {
        Write-Error "Fichier non trouve: $FilePath"
        return
    }
    
    $acl = Get-Acl $FilePath
    
    Write-Host ""
    Write-Host "Proprietaire: $($acl.Owner)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Permissions:" -ForegroundColor Yellow
    
    $acl.Access | ForEach-Object {
        $typeSymbol = if ($_.AccessControlType -eq "Allow") { "+" } else { "-" }
        $typeColor = if ($_.AccessControlType -eq "Allow") { "Green" } else { "Red" }
        
        Write-Host "  $typeSymbol $($_.IdentityReference)" -ForegroundColor $typeColor
        Write-Host "    Droits: $($_.FileSystemRights)" -ForegroundColor White
        Write-Host ""
    }
}

# Version tableau pour plusieurs fichiers
function Get-MultipleFilePermissions {
    param([string[]]$FilePaths)
    
    $results = @()
    
    foreach ($path in $FilePaths) {
        if (Test-Path $path) {
            $acl = Get-Acl $path
            $file = Get-Item $path
            
            $results += [PSCustomObject]@{
                Fichier = $file.Name
                Proprietaire = $acl.Owner
                Taille = $file.Length
                Modifie = $file.LastWriteTime
                NbPermissions = ($acl.Access | Measure-Object).Count
                LectureSeule = $file.IsReadOnly
            }
        }
    }
    
    $results | Format-Table -AutoSize
}

# Exemples d'utilisation :
Write-Host "=== EXEMPLES D'UTILISATION ===" -ForegroundColor Magenta
Write-Host ""
Write-Host "1. Analyse complete d'un fichier :" -ForegroundColor Yellow
Write-Host "   Show-FilePermissions 'mon_fichier.txt'"
Write-Host ""
Write-Host "2. Affichage simplifie :" -ForegroundColor Yellow
Write-Host "   Get-FilePermissionsSimple 'mon_fichier.txt'"
Write-Host ""
Write-Host "3. Analyse de plusieurs fichiers :" -ForegroundColor Yellow
Write-Host "   Get-MultipleFilePermissions @('fichier1.txt', 'fichier2.exe')"
Write-Host ""
Write-Host "4. Tous les fichiers du dossier actuel :" -ForegroundColor Yellow
Write-Host "   Get-ChildItem | ForEach-Object { Get-FilePermissionsSimple `$_.FullName }"
Write-Host ""

# Si un fichier est passe en parametre au script
if ($args.Count -gt 0) {
    Show-FilePermissions $args[0]
}