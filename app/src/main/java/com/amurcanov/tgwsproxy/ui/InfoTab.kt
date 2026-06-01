package com.amurcanov.tgwsproxy.ui

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.Build
import android.widget.Toast
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ContentCopy
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Security
import androidx.compose.material.icons.filled.Troubleshoot
import androidx.compose.material3.Button
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.amurcanov.tgwsproxy.BuildConfig
import com.amurcanov.tgwsproxy.LogEntry
import com.amurcanov.tgwsproxy.LogManager
import com.amurcanov.tgwsproxy.ProxyService
import com.amurcanov.tgwsproxy.SettingsStore

@Composable
fun InfoTab(settingsStore: SettingsStore) {
    val context = LocalContext.current
    val t = appStrings()
    val savedPort by settingsStore.port.collectAsStateWithLifecycle(initialValue = "1443")
    val savedPoolSize by settingsStore.poolSize.collectAsStateWithLifecycle(initialValue = 4)
    val savedRouteProvider by settingsStore.routeProvider.collectAsStateWithLifecycle(initialValue = SettingsStore.ROUTE_SMART)
    val savedCfEnabled by settingsStore.cfproxyEnabled.collectAsStateWithLifecycle(initialValue = true)
    val savedCustomCfDomainEnabled by settingsStore.customCfDomainEnabled.collectAsStateWithLifecycle(initialValue = false)
    val savedCustomCfDomain by settingsStore.customCfDomain.collectAsStateWithLifecycle(initialValue = "")
    val currentLogs by LogManager.logs.collectAsStateWithLifecycle()
    val routeHealth by ProxyService.routeHealth.collectAsStateWithLifecycle()
    val reportText = buildSupportReport(
        t = t,
        context = context,
        port = savedPort,
        poolSize = savedPoolSize,
        routeProvider = savedRouteProvider,
        cfEnabled = savedCfEnabled,
        customCfDomainEnabled = savedCustomCfDomainEnabled,
        customCfDomain = savedCustomCfDomain,
        routeHealth = routeHealth,
        logs = currentLogs
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(start = 16.dp, end = 16.dp, top = 0.dp, bottom = 28.dp)
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .height(48.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = t.info,
                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold),
                color = MaterialTheme.colorScheme.onSurface
            )
        }

        AppSectionCard {
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp), verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.Security, contentDescription = null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(28.dp))
                Text("WhiteDns TG", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Black)
            }
            Text(
                text = t.appSummary,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        AppSectionCard {
            HelpRow(t.quickStartTitle, t.quickStartHelp)
            HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.35f))
            HelpRow(t.privateDomainTitle, t.privateDomainUsageHelp)
            HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.35f))
            HelpRow(t.googleDomainTitle, t.googleDomainUsageHelp)
            HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.35f))
            HelpRow(t.validateDomainTitle, t.validateDomainUsageHelp)
        }

        AppSectionCard {
            HelpRow(t.cloudflareTitle, t.cloudflareHelp)
            HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.35f))
            HelpRow(t.wsPool, t.poolHelp)
            HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.35f))
            HelpRow(t.secretKey, t.secretHelp)
            HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.35f))
            HelpRow(t.repair, t.routeHelp)
        }

        AppSectionCard {
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.Troubleshoot, contentDescription = null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(22.dp))
                Text(t.supportReport, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            }
            Text(
                text = if (LocalAppLanguage.current == AppLanguage.Farsi) {
                    "گزارش شامل تنظیمات فنی و خطاهای اخیر است. کلید مخفی داخل گزارش قرار نمی‌گیرد."
                } else {
                    "The report includes technical settings and recent errors. It does not include your secret key."
                },
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Button(
                onClick = {
                    val clipboard = context.getSystemService(ClipboardManager::class.java)
                    clipboard?.setPrimaryClip(ClipData.newPlainText("WhiteDns TG report", reportText))
                    Toast.makeText(context, t.reportCopied, Toast.LENGTH_SHORT).show()
                },
                modifier = Modifier.fillMaxWidth().height(52.dp),
                shape = RoundedCornerShape(24.dp)
            ) {
                Icon(Icons.Default.ContentCopy, contentDescription = null, modifier = Modifier.size(18.dp))
                Spacer(Modifier.size(8.dp))
                Text(t.copy, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
private fun HelpRow(title: String, text: String) {
    Row(horizontalArrangement = Arrangement.spacedBy(12.dp), verticalAlignment = Alignment.Top) {
        Icon(Icons.Default.Info, contentDescription = null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(20.dp))
        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(title, style = MaterialTheme.typography.titleSmall, color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
            Text(text, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}

private fun buildSupportReport(
    t: AppStrings,
    context: Context,
    port: String,
    poolSize: Int,
    routeProvider: String,
    cfEnabled: Boolean,
    customCfDomainEnabled: Boolean,
    customCfDomain: String,
    routeHealth: String,
    logs: List<LogEntry>
): String {
    val mode = when (routeProvider) {
        SettingsStore.ROUTE_SMART -> "Smart CDN"
        SettingsStore.ROUTE_PRIVATE_FRONT -> "Private front"
        SettingsStore.ROUTE_GOOGLE_FRONT -> "Google front"
        SettingsStore.ROUTE_DIRECT -> "Direct DC"
        else -> if (cfEnabled) "Cloudflare" else "Direct"
    }
    val cfDomainLine = if (cfEnabled && customCfDomainEnabled && customCfDomain.isNotBlank()) {
        "\nCF domain: ${customCfDomain.trim()}"
    } else {
        ""
    }
    val recentErrors = logs.asReversed().filter { it.priority >= 5 }.take(10)
    val errorsBlock = if (recentErrors.isEmpty()) {
        "none"
    } else {
        recentErrors.joinToString("\n") { entry -> "- ${entry.message}${if (entry.count > 1) " (x${entry.count})" else ""}" }
    }

    return buildString {
        appendLine("App: WhiteDns TG ${BuildConfig.VERSION_NAME}")
        appendLine("Android: ${Build.VERSION.RELEASE ?: "?"} (SDK ${Build.VERSION.SDK_INT})")
        appendLine("Device: ${Build.MANUFACTURER} / ${Build.MODEL}")
        appendLine("ABI: ${Build.SUPPORTED_ABIS.joinToString().ifBlank { "unknown" }}")
        appendLine("Network: ${networkType(context)}")
        appendLine("${t.settings}:")
        appendLine("Mode: $mode")
        appendLine("WS pool: $poolSize")
        append("Port: ${port.trim().ifBlank { "1443" }}")
        append(cfDomainLine)
        appendLine()
        appendLine("Last route health: ${routeHealth.ifBlank { "unknown" }}")
        appendLine()
        appendLine("Recent errors:")
        append(errorsBlock)
    }.trim()
}

private fun networkType(context: Context): String {
    return try {
        val manager = context.getSystemService(ConnectivityManager::class.java) ?: return "unknown"
        val network = manager.activeNetwork ?: return "offline"
        val caps = manager.getNetworkCapabilities(network) ?: return "unknown"
        when {
            caps.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> "cellular"
            caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> "wifi"
            caps.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) -> "ethernet"
            caps.hasTransport(NetworkCapabilities.TRANSPORT_VPN) -> "vpn"
            else -> "other"
        }
    } catch (_: SecurityException) {
        "unknown"
    } catch (_: RuntimeException) {
        "unknown"
    }
}
