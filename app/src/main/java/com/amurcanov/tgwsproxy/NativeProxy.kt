package com.amurcanov.tgwsproxy

import com.sun.jna.Library
import com.sun.jna.Native
import com.sun.jna.Pointer

interface ProxyLibrary : Library {
    companion object {
        val INSTANCE = Native.load("tgwsproxy", ProxyLibrary::class.java) as ProxyLibrary
    }

    fun StartProxy(host: String, port: Int, dcIps: String, secret: String, verbose: Int): Int
    fun StopProxy(): Int
    fun SetPoolSize(size: Int)
    fun SetCfProxyCacheDir(cacheDir: String)
    fun SetCfProxyConfig(enabled: Int, priority: Int, userDomain: String)
    fun SetFakeTls(enabled: Int, domain: String)
    fun CheckLocalPort(): Int
    fun ProbeRoute(): Pointer?
    fun ValidateFrontDomain(domain: String): Pointer?
    fun RotateCfProxyDomain(): Int
    fun GetSecretWithPrefix(): Pointer?
    fun GetStats(): Pointer?
    fun FreeString(p: Pointer)
}

object NativeProxy {
    fun startProxy(host: String, port: Int, dcIps: String, secret: String, verbose: Int): Int {
        return ProxyLibrary.INSTANCE.StartProxy(host, port, dcIps, secret, verbose)
    }

    fun stopProxy(): Int {
        return ProxyLibrary.INSTANCE.StopProxy()
    }

    fun setPoolSize(size: Int) {
        ProxyLibrary.INSTANCE.SetPoolSize(size)
    }

    fun setCfProxyCacheDir(cacheDir: String) {
        ProxyLibrary.INSTANCE.SetCfProxyCacheDir(cacheDir)
    }

    fun setCfProxyConfig(enabled: Boolean, priority: Boolean, userDomain: String) {
        ProxyLibrary.INSTANCE.SetCfProxyConfig(
            if (enabled) 1 else 0,
            if (priority) 1 else 0,
            userDomain
        )
    }

    fun setFakeTls(enabled: Boolean, domain: String = "") {
        ProxyLibrary.INSTANCE.SetFakeTls(if (enabled) 1 else 0, domain)
    }

    fun checkLocalPort(): Boolean {
        return ProxyLibrary.INSTANCE.CheckLocalPort() == 1
    }

    fun probeRoute(): String? {
        val ptr = ProxyLibrary.INSTANCE.ProbeRoute() ?: return null
        val res = ptr.getString(0)
        ProxyLibrary.INSTANCE.FreeString(ptr)
        return res
    }

    fun validateFrontDomain(domain: String): String? {
        val ptr = ProxyLibrary.INSTANCE.ValidateFrontDomain(domain) ?: return null
        val res = ptr.getString(0)
        ProxyLibrary.INSTANCE.FreeString(ptr)
        return res
    }

    fun rotateCfProxyDomain(): Boolean {
        return ProxyLibrary.INSTANCE.RotateCfProxyDomain() == 1
    }

    /** Returns the full secret with correct prefix (dd or ee+domain_hex) */
    fun getSecretWithPrefix(): String? {
        val ptr = ProxyLibrary.INSTANCE.GetSecretWithPrefix() ?: return null
        val res = ptr.getString(0)
        ProxyLibrary.INSTANCE.FreeString(ptr)
        return res
    }

    fun getStats(): String? {
        val ptr = ProxyLibrary.INSTANCE.GetStats() ?: return null
        val res = ptr.getString(0)
        ProxyLibrary.INSTANCE.FreeString(ptr)
        return res
    }

}
