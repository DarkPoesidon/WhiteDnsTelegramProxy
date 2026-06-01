package com.amurcanov.tgwsproxy.ui

import android.content.Context
import java.net.InetSocketAddress
import java.net.Socket
import android.widget.Toast
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.Image
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ContentCopy
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.ColorFilter
import androidx.compose.ui.graphics.ColorMatrix
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.amurcanov.tgwsproxy.BuildConfig
import com.amurcanov.tgwsproxy.NativeProxy
import com.amurcanov.tgwsproxy.ProxyController
import com.amurcanov.tgwsproxy.ProxyService
import com.amurcanov.tgwsproxy.SettingsStore
import com.amurcanov.tgwsproxy.R
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

@Composable
fun ConnectionTab(settingsStore: SettingsStore) {
    val context = LocalContext.current
    val t = appStrings()
    val isRunning by ProxyService.isRunning.collectAsStateWithLifecycle()
    val serviceRouteHealth by ProxyService.routeHealth.collectAsStateWithLifecycle()

    val isReady by settingsStore.isReady.collectAsStateWithLifecycle(initialValue = false)

    // Settings
    val savedPort by settingsStore.port.collectAsStateWithLifecycle(initialValue = "1443")
    val savedRouteProvider by settingsStore.routeProvider.collectAsStateWithLifecycle(initialValue = SettingsStore.ROUTE_SMART)
    val savedCfEnabled by settingsStore.cfproxyEnabled.collectAsStateWithLifecycle(initialValue = true)
    val savedPoolSize by settingsStore.poolSize.collectAsStateWithLifecycle(initialValue = 4)
    val savedSecretKey by settingsStore.secretKey.collectAsStateWithLifecycle(initialValue = "LOADING")

    val scope = rememberCoroutineScope()
    val currentVersion = remember { "v${BuildConfig.VERSION_NAME.removePrefix("v")}" }

    if (!isReady || savedSecretKey == "LOADING") {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator(
                color = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(24.dp),
                strokeWidth = 2.dp
            )
        }
        return
    }

    // Auto-generate secret if empty
    LaunchedEffect(savedSecretKey) {
        if (savedSecretKey == "") {
            val bytes = ByteArray(16)
            java.security.SecureRandom().nextBytes(bytes)
            val generated = bytes.joinToString("") { "%02x".format(it) }
            scope.launch { settingsStore.saveSecretKey(generated) }
        }
    }

    var isStarting by remember { mutableStateOf(false) }
    val statusText = when {
        isStarting -> t.connecting
        isRunning -> t.connected
        else -> t.disconnected
    }

    LaunchedEffect(isRunning) {
        if (isRunning) {
            delay(600)
            isStarting = false
        }
        if (!isRunning) {
            isStarting = false
        }
    }

    val port = savedPort.toIntOrNull() ?: 1443
    val secretForUrl = remember(savedSecretKey) {
        val raw = savedSecretKey.trim()
        if (raw.isNotEmpty() && raw != "LOADING") raw else "00000000000000000000000000000000"
    }
    val proxyUrl = "https://t.me/proxy?server=127.0.0.1&port=$port&secret=dd$secretForUrl"
    var routeStatus by remember(t) { mutableStateOf(t.routeNotChecked) }
    var isCheckingRoute by remember { mutableStateOf(false) }
    val isRouteHealthy = serviceRouteHealth.startsWith("ok=1")

    LaunchedEffect(isRunning, port) {
        while (isRunning) {
            if (serviceRouteHealth == "state=starting") {
                routeStatus = readLocalProxyStatus(port, t)
            }
            delay(5000)
        }
        routeStatus = t.proxyStopped
    }

    LaunchedEffect(serviceRouteHealth, isRunning, t) {
        if (isRunning) {
            routeStatus = serviceRouteHealth.toFriendlyHealthStatus(t)
        }
    }

    val connectAction = {
        if (!isRunning && !isStarting) {
            isStarting = true
            scope.launch {
                val started = ProxyController.startFromSavedSettings(
                    context = context,
                    showInvalidPortToast = true
                )
                if (!started) {
                    isStarting = false
                }
            }
        }
    }

    val disconnectAction = {
        if (isRunning || isStarting) {
            ProxyController.stop(context)
        }
    }

    val isActiveVisual = isRunning || isStarting
    val logoScale by animateFloatAsState(
        targetValue = if (isActiveVisual) 1.12f else 0.94f,
        animationSpec = tween(durationMillis = 650, easing = CubicBezierEasing(0.22f, 1f, 0.36f, 1f)),
        label = "logo_scale"
    )
    val logoInteractionSource = remember { MutableInteractionSource() }
    val statusColor by animateColorAsState(
        targetValue = if (isActiveVisual) {
            MaterialTheme.colorScheme.primary
        } else {
            MaterialTheme.colorScheme.onSurfaceVariant
        },
        label = "connection_status_color"
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 20.dp)
            .padding(top = 0.dp, bottom = 16.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .height(48.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = t.launch,
                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold),
                color = MaterialTheme.colorScheme.onSurface
            )
        }

        Spacer(modifier = Modifier.height(8.dp))

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f),
            contentAlignment = Alignment.Center
        ) {
            AppSectionCard(
                modifier = Modifier
                    .fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth(),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Image(
                        painter = painterResource(id = R.drawable.brand_logo),
                        contentDescription = null,
                        modifier = Modifier
                            .size(180.dp)
                            .clip(RoundedCornerShape(40.dp))
                            .clickable(
                                interactionSource = logoInteractionSource,
                                indication = null,
                                onClick = if (isActiveVisual) disconnectAction else connectAction
                            )
                            .scale(logoScale),
                        colorFilter = if (isActiveVisual) null else ColorFilter.colorMatrix(ColorMatrix().apply { setToSaturation(0f) }),
                        alpha = if (isActiveVisual) 1f else 0.52f
                    )
                    Text(
                        text = statusText,
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Bold,
                        color = statusColor,
                        textAlign = TextAlign.Center
                    )

                    Column(
                        modifier = Modifier.fillMaxWidth(),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Button(
                            onClick = { openTelegram(context, proxyUrl, t.telegramNotFound) },
                            enabled = isRunning && isRouteHealthy,
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(52.dp),
                            shape = RoundedCornerShape(24.dp),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = MaterialTheme.colorScheme.primaryContainer,
                                contentColor = MaterialTheme.colorScheme.onPrimaryContainer,
                                disabledContainerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f),
                                disabledContentColor = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.25f)
                            )
                        ) {
                            Text(
                                t.applyTelegram,
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.SemiBold
                            )
                        }

                        ProxyStatusPanel(
                            routeLabel = routeLabel(savedRouteProvider, savedCfEnabled, t),
                            poolSize = savedPoolSize,
                            port = savedPort,
                            version = currentVersion,
                            routeStatus = routeStatus,
                            routeHealth = serviceRouteHealth,
                            isRunning = isRunning,
                            isCheckingRoute = isCheckingRoute,
                            onCheckRoute = {
                                if (!isCheckingRoute) {
                                    isCheckingRoute = true
                                    scope.launch {
                                        val raw = probeRoute(isRunning)
                                        if (raw.isNotBlank()) {
                                            ProxyService.publishRouteHealth(raw)
                                        }
                                        routeStatus = raw.toFriendlyHealthStatus(t)
                                        isCheckingRoute = false
                                    }
                                }
                            },
                            onRepairRoute = {
                                if (isRunning) {
                                    routeStatus = t.restartingRoute
                                    ProxyController.restart(context)
                                } else {
                                    connectAction()
                                }
                            }
                        )

                        Surface(
                            onClick = {
                                val cb = context.getSystemService(Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager
                                cb.setPrimaryClip(android.content.ClipData.newPlainText("Proxy", proxyUrl))
                                Toast.makeText(context, t.copied, Toast.LENGTH_SHORT).show()
                            },
                            shape = RoundedCornerShape(24.dp),
                            color = MaterialTheme.colorScheme.surface,
                            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.3f)),
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(56.dp)
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                modifier = Modifier
                                    .fillMaxSize()
                                    .padding(horizontal = 16.dp)
                            ) {
                                Text(
                                    text = proxyUrl,
                                    style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.Medium),
                                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.8f),
                                    maxLines = 1,
                                    modifier = Modifier.weight(1f)
                                )
                                Icon(
                                    Icons.Default.ContentCopy,
                                    contentDescription = t.copy,
                                    tint = MaterialTheme.colorScheme.primary,
                                    modifier = Modifier.size(20.dp)
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun ProxyStatusPanel(
    routeLabel: String,
    poolSize: Int,
    port: String,
    version: String,
    routeStatus: String,
    routeHealth: String,
    isRunning: Boolean,
    isCheckingRoute: Boolean,
    onCheckRoute: () -> Unit,
    onRepairRoute: () -> Unit
) {
    val t = appStrings()
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Surface(
            shape = RoundedCornerShape(22.dp),
            color = MaterialTheme.colorScheme.surface,
            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.3f)),
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(IntrinsicSize.Min)
                    .padding(horizontal = 4.dp, vertical = 2.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                ProxyStatusItem(
                    text = routeLabel,
                    modifier = Modifier
                        .weight(0.9f)
                        .padding(horizontal = 6.dp, vertical = 8.dp)
                )
                ProxyStatusDivider()
                ProxyStatusItem(
                    text = "${t.pool} x$poolSize",
                    modifier = Modifier
                        .weight(1.05f)
                        .padding(horizontal = 6.dp, vertical = 8.dp)
                )
                ProxyStatusDivider()
                ProxyStatusItem(
                    text = "${t.port} $port",
                    modifier = Modifier
                        .weight(1.35f)
                        .padding(horizontal = 6.dp, vertical = 8.dp)
                )
                ProxyStatusDivider()
                ProxyStatusItem(
                    text = version,
                    modifier = Modifier
                        .weight(1.1f)
                        .padding(horizontal = 6.dp, vertical = 8.dp)
                )
            }
        }

        Surface(
            shape = RoundedCornerShape(22.dp),
            color = MaterialTheme.colorScheme.surface,
            border = BorderStroke(
                1.dp,
                when {
                    routeHealth.startsWith("ok=1") -> MaterialTheme.colorScheme.primary.copy(alpha = 0.78f)
                    routeHealth.startsWith("ok=0") -> MaterialTheme.colorScheme.error.copy(alpha = 0.78f)
                    else -> MaterialTheme.colorScheme.outline.copy(alpha = 0.24f)
                }
            ),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(
                modifier = Modifier.fillMaxWidth().padding(14.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                Text(
                    text = routeStatus,
                    style = MaterialTheme.typography.bodySmall,
                    fontWeight = FontWeight.Medium,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.82f),
                    maxLines = 3
                )
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(
                        onClick = onCheckRoute,
                        enabled = isRunning && !isCheckingRoute,
                        modifier = Modifier.weight(1f).height(44.dp),
                        shape = RoundedCornerShape(22.dp)
                    ) {
                        Text(if (isCheckingRoute) t.checking else t.check, fontWeight = FontWeight.SemiBold)
                    }
                    Button(
                        onClick = onRepairRoute,
                        modifier = Modifier.weight(1f).height(44.dp),
                        shape = RoundedCornerShape(22.dp)
                    ) {
                        Text(t.repair, fontWeight = FontWeight.SemiBold)
                    }
                }
            }
        }
    }
}

private fun readLocalProxyStatus(port: Int, t: AppStrings): String {
    val nativeLocalOk = try {
        NativeProxy.checkLocalPort()
    } catch (_: Throwable) {
        false
    }
    val localOk = nativeLocalOk || canConnectLocal("127.0.0.1", port) || canConnectLocal("localhost", port)

    if (!localOk) {
        return "${t.localPortBad}. ${t.repair}"
    }
    return t.localProxyReady
}

private fun canConnectLocal(host: String, port: Int): Boolean {
    return try {
        Socket().use { socket ->
            socket.connect(InetSocketAddress(host, port), 1200)
            true
        }
    } catch (_: Exception) {
        false
    }
}

private fun probeRoute(isRunning: Boolean): String {
    if (!isRunning) {
        return "state=stopped"
    }
    return try {
        NativeProxy.probeRoute().orEmpty()
    } catch (_: Throwable) {
        "ok=0 stage=probe err=native_probe_failed"
    }
}

private fun String.toFriendlyHealthStatus(t: AppStrings): String {
    if (isBlank()) return t.routeProbeFailed
    val parts = split(" ").mapNotNull {
        val idx = it.indexOf("=")
        if (idx <= 0) null else it.substring(0, idx) to it.substring(idx + 1)
    }.toMap()
    return when (parts["state"]) {
        "starting" -> t.routeTesting
        "restarting", "repairing" -> t.autoRepairing
        "stopped" -> t.proxyStopped
        else -> toFriendlyProbeStatus(t)
    }
}

private fun String.toFriendlyProbeStatus(t: AppStrings): String {
    val parts = split(" ").mapNotNull {
        val idx = it.indexOf("=")
        if (idx <= 0) null else it.substring(0, idx) to it.substring(idx + 1)
    }.toMap()
    val ok = parts["ok"] == "1"
    val stage = parts["stage"].orEmpty()
    val active = parts["active"]?.takeIf { it.isNotBlank() && it != "-" }
    val prefix = if (ok) t.routeOk else t.routeFailed
    val route = when (stage) {
        "cf" -> active?.let { "Cloudflare: $it" } ?: "Cloudflare"
        "tcp" -> active?.let { "TCP: $it" } ?: "TCP ${t.direct}"
        "local" -> t.localPortBad
        else -> t.auto
    }
    val err = parts["err"]?.replace('_', ' ')
    return if (err.isNullOrBlank()) "$prefix. $route" else "$prefix. $route. $err"
}

private fun routeLabel(routeProvider: String, cfEnabled: Boolean, t: AppStrings): String {
    return when (routeProvider) {
        SettingsStore.ROUTE_SMART -> t.smartRoute
        SettingsStore.ROUTE_PRIVATE_FRONT -> t.privateFront
        SettingsStore.ROUTE_GOOGLE_FRONT -> "Google"
        SettingsStore.ROUTE_DIRECT -> t.direct
        else -> if (cfEnabled) t.smartRoute else t.direct
    }
}

@Composable
private fun ProxyStatusItem(
    text: String,
    modifier: Modifier = Modifier,
) {
    Box(
        modifier = modifier,
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.labelMedium,
            fontWeight = FontWeight.SemiBold,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.8f),
            textAlign = TextAlign.Center,
            maxLines = 1,
            modifier = Modifier.fillMaxWidth()
        )
    }
}

@Composable
private fun ProxyStatusDivider() {
    Box(
        modifier = Modifier
            .fillMaxHeight()
            .width(1.dp)
            .background(MaterialTheme.colorScheme.onSurface.copy(alpha = 0.12f))
    )
}
